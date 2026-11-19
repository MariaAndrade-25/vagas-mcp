# Conector MCP de vagas

Reúne vagas da Adzuna, Jooble e Remotive em um formato único. O Claude lê o seu
perfil e pontua a compatibilidade de cada vaga (ex.: só mostrar 80+).

## Ferramentas
- `buscar_vagas(cargo, local, incluir_remotas, limite_por_fonte)`
- `detalhar_vaga(id)`

## 1. Chaves de API
- Adzuna: crie conta em https://developer.adzuna.com/ (app_id e app_key)
- Jooble: peça a chave em https://jooble.org/api/about
- Remotive: não precisa de chave
Fontes sem chave são ignoradas automaticamente.

## 2. Teste local
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export AUTH_TOKEN=meu-token ADZUNA_APP_ID=... ADZUNA_APP_KEY=... JOOBLE_KEY=...
python server.py
```
Em outro terminal, abra o inspetor:
```bash
npx @modelcontextprotocol/inspector
```
Escolha o transporte "Streamable HTTP", URL `http://localhost:8080/mcp`, e
adicione o cabeçalho `Authorization: Bearer meu-token`. Teste `buscar_vagas`.
(O endereço `/health` responde sem token, para checagem de saúde.)

## 3. Deploy (exemplo: Google Cloud Run)
```bash
gcloud run deploy vagas-mcp --source . --region southamerica-east1 \
  --allow-unauthenticated \
  --set-env-vars AUTH_TOKEN=...,ADZUNA_APP_ID=...,ADZUNA_APP_KEY=...,ADZUNA_COUNTRY=br,JOOBLE_KEY=...
```
`--allow-unauthenticated` só abre a porta de rede; quem protege o acesso é o
`AUTH_TOKEN`. Em Fly.io ou Render, use o Dockerfile e cadastre as mesmas
variáveis de ambiente (segredos) no painel.

A URL final do conector será `https://SEU-SERVICO/mcp`.

## 4. Adicionar ao Claude
Customize > Connectors > Add custom connector:
- Nome: Vagas
- URL: `https://SEU-SERVICO/mcp`
- Request headers: `Authorization` com o valor `Bearer SEU_TOKEN`
  (a Anthropic aprova cada nome de cabeçalho; se `Authorization` for recusado,
  ajuste o código para outro cabeçalho aprovado)

## 5. Como usar
"Meu perfil: [cole o currículo ou resumo]. Busque vagas de [cargo] em [local],
leia a descrição das mais promissoras com detalhar_vaga, pontue de 0 a 100 por
(habilidades obrigatórias 40, senioridade 20, desejáveis 15, local/modalidade
15, salário/preferências 10) e mostre só as de 80 ou mais, com o motivo da nota."

## Observações
- O cache de `detalhar_vaga` é em memória. Se o serviço escalar para várias
  instâncias ou reiniciar, rode `buscar_vagas` de novo.
- Respeite os termos de uso de cada API.
