"""Conector MCP de vagas: reúne Adzuna, Jooble e Remotive em um formato único.

A pontuação de compatibilidade (ex.: 80%+) fica a cargo do Claude, que compara
o seu perfil com a descrição de cada vaga devolvida por estas ferramentas.
"""
import asyncio
import hashlib
import html
import os
import re

import httpx
import uvicorn
from mcp.server.fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.environ.get("ADZUNA_APP_KEY", "")
ADZUNA_COUNTRY = os.environ.get("ADZUNA_COUNTRY", "br")
JOOBLE_KEY = os.environ.get("JOOBLE_KEY", "")
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "")
PORT = int(os.environ.get("PORT", "8080"))

MAX_DESC_LISTA = 600  # trecho curto na listagem, para economizar contexto
TIMEOUT = httpx.Timeout(15.0)

mcp = FastMCP("vagas", host="0.0.0.0", port=PORT, stateless_http=True)

# Cache em memória: id -> vaga completa (usado por detalhar_vaga).
# Em hospedagem com várias instâncias, o cache pode não ser compartilhado;
# nesse caso detalhar_vaga avisa e a vaga pode ser buscada de novo.
_CACHE: dict[str, dict] = {}


def _limpar_html(texto: str) -> str:
    texto = re.sub(r"<[^>]+>", " ", texto or "")
    texto = html.unescape(texto)
    return re.sub(r"\s+", " ", texto).strip()


def _id(fonte: str, bruto: str) -> str:
    return fonte[:3] + "_" + hashlib.sha1(f"{fonte}:{bruto}".encode()).hexdigest()[:10]


def _vaga(fonte, bruto_id, titulo, empresa, local, salario, link, descricao) -> dict:
    return {
        "id": _id(fonte, str(bruto_id or link)),
        "fonte": fonte,
        "titulo": (titulo or "").strip(),
        "empresa": (empresa or "").strip(),
        "local": (local or "").strip(),
        "salario": (salario or "").strip(),
        "link": link or "",
        "descricao": _limpar_html(descricao),
    }


async def _adzuna(client, cargo, local, limite):
    if not (ADZUNA_APP_ID and ADZUNA_APP_KEY):
        return []
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": cargo,
        "results_per_page": limite,
        "content-type": "application/json",
    }
    if local:
        params["where"] = local
    r = await client.get(
        f"https://api.adzuna.com/v1/api/jobs/{ADZUNA_COUNTRY}/search/1", params=params
    )
    r.raise_for_status()
    saida = []
    for j in r.json().get("results", []):
        lo, hi = j.get("salary_min"), j.get("salary_max")
        salario = f"{int(lo)}-{int(hi)}" if lo and hi else ""
        saida.append(
            _vaga(
                "adzuna",
                j.get("id"),
                j.get("title"),
                (j.get("company") or {}).get("display_name"),
                (j.get("location") or {}).get("display_name"),
                salario,
                j.get("redirect_url"),
                j.get("description"),
            )
        )
    return saida


async def _jooble(client, cargo, local, limite):
    if not JOOBLE_KEY:
        return []
    r = await client.post(
        f"https://jooble.org/api/{JOOBLE_KEY}",
        json={"keywords": cargo, "location": local, "page": 1},
    )
    r.raise_for_status()
    saida = []
    for j in r.json().get("jobs", [])[:limite]:
        saida.append(
            _vaga(
                "jooble",
                j.get("id"),
                j.get("title"),
                j.get("company"),
                j.get("location"),
                j.get("salary"),
                j.get("link"),
                j.get("snippet"),
            )
        )
    return saida


async def _remotive(client, cargo, limite):
    r = await client.get(
        "https://remotive.com/api/remote-jobs", params={"search": cargo, "limit": limite}
    )
    r.raise_for_status()
    saida = []
    for j in r.json().get("jobs", [])[:limite]:
        saida.append(
            _vaga(
                "remotive",
                j.get("id"),
                j.get("title"),
                j.get("company_name"),
                j.get("candidate_required_location"),
                j.get("salary"),
                j.get("url"),
                j.get("description"),
            )
        )
    return saida


@mcp.tool()
async def buscar_vagas(
    cargo: str, local: str = "", incluir_remotas: bool = True, limite_por_fonte: int = 15
) -> dict:
    """Busca vagas em várias fontes (Adzuna, Jooble, Remotive) e devolve uma
    lista unificada e sem duplicatas. Cada vaga traz id, fonte, titulo, empresa,
    local, salario, link e um trecho da descricao. Use detalhar_vaga(id) para
    ler a descrição completa antes de avaliar a compatibilidade com o perfil.

    cargo: palavras-chave do cargo, ex.: "analista de dados".
    local: cidade ou estado, ex.: "São Paulo" (vazio = qualquer lugar).
    incluir_remotas: inclui o feed Remotive (vagas 100% remotas).
    limite_por_fonte: máximo de vagas por fonte (1 a 30).
    """
    limite = max(1, min(limite_por_fonte, 30))
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        tarefas = {
            "adzuna": _adzuna(client, cargo, local, limite),
            "jooble": _jooble(client, cargo, local, limite),
        }
        if incluir_remotas:
            tarefas["remotive"] = _remotive(client, cargo, limite)
        resultados = await asyncio.gather(*tarefas.values(), return_exceptions=True)

    vagas, avisos, vistos = [], [], set()
    for fonte, res in zip(tarefas.keys(), resultados):
        if isinstance(res, Exception):
            avisos.append(f"{fonte}: falhou ({type(res).__name__})")
            continue
        for v in res:
            chave = (v["titulo"].lower(), v["empresa"].lower())
            if chave in vistos or not v["link"]:
                continue
            vistos.add(chave)
            _CACHE[v["id"]] = v
            vagas.append({**v, "descricao": v["descricao"][:MAX_DESC_LISTA]})

    if not (ADZUNA_APP_ID and ADZUNA_APP_KEY):
        avisos.append("adzuna: sem chaves configuradas (ignorada)")
    if not JOOBLE_KEY:
        avisos.append("jooble: sem chave configurada (ignorada)")
    return {"total": len(vagas), "vagas": vagas, "avisos": avisos}


@mcp.tool()
async def detalhar_vaga(id: str) -> dict:
    """Devolve a descrição completa de uma vaga retornada por buscar_vagas,
    para checar requisitos, senioridade e benefícios."""
    vaga = _CACHE.get(id)
    if not vaga:
        return {"erro": "Vaga não encontrada no cache. Rode buscar_vagas novamente."}
    return vaga


class TokenAuth(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path == "/health":
            return JSONResponse({"ok": True})
        if AUTH_TOKEN and request.headers.get("authorization") != f"Bearer {AUTH_TOKEN}":
            return JSONResponse({"erro": "nao autorizado"}, status_code=401)
        return await call_next(request)


app = mcp.streamable_http_app()
app.add_middleware(TokenAuth)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
