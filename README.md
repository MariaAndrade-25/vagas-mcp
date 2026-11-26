# Vagas MCP

<p align="center">

<img width="346" height="260" alt="WorkHeresGIF" src="https://github.com/user-attachments/assets/9cea1029-1614-4538-bd16-0bd7e4235292" />
</p>

**Um conector MCP para buscar, centralizar e analisar vagas de emprego em diferentes plataformas.**

O Vagas MCP reúne oportunidades de emprego de **Adzuna, Jooble e Remotive** em um único lugar, permitindo que assistentes de IA como o Claude pesquisem vagas, consultem descrições completas e avaliem a compatibilidade com o perfil profissional do usuário.

A proposta é simplificar a busca por oportunidades: em vez de acessar vários sites e comparar cada vaga manualmente, você informa seu currículo, define os critérios desejados e recebe uma seleção de oportunidades alinhadas aos seus objetivos profissionais.

---

## Sumário

- [Como funciona](#como-funciona)
- [Funcionalidades](#funcionalidades)
- [Ferramentas MCP](#ferramentas-mcp)
- [Exemplo de uso](#exemplo-de-uso)
- [Dois modos de uso: local ou online](#dois-modos-de-uso-local-ou-online)
- [Configuração das APIs](#configuração-das-apis)
- [Instalação](#instalação)
- [Modo local (Claude Desktop)](#modo-local-claude-desktop)
- [Modo online (servidor HTTP)](#modo-online-servidor-http)
- [Testando o servidor](#testando-o-servidor)
- [Solução de problemas](#solução-de-problemas)
- [Segurança](#segurança)
- [Destaques técnicos](#destaques-técnicos)
- [Limitações conhecidas](#limitações-conhecidas)
- [Estrutura do projeto](#estrutura-do-projeto)

---

## Como funciona

```text
                         ┌──────────────┐
                         │    Claude    │
                         └──────┬───────┘
                                │
              ┌─────────────────┴─────────────────┐
              │                                   │
   Modo local (stdio)                  Modo online (Streamable HTTP)
   Claude Desktop inicia               Servidor publicado na nuvem
   o programa no seu PC                (ex.: Render), endpoint /mcp
              │                                   │
              └─────────────────┬─────────────────┘
                                ▼
                    ┌─────────────────────┐
                    │      Vagas MCP      │
                    └──────────┬──────────┘
                               │
               ┌───────────────┼───────────────┐
               ▼               ▼               ▼
         ┌──────────┐    ┌──────────┐    ┌──────────┐
         │  Adzuna  │    │  Jooble  │    │ Remotive │
         └──────────┘    └──────────┘    └──────────┘
```

### Fluxo de busca

1. O usuário informa seu currículo, cargo desejado, localização e preferências.
2. O Claude utiliza a ferramenta `buscar_vagas` para consultar as fontes disponíveis.
3. O servidor agrega e normaliza os resultados em um formato único, removendo duplicatas.
4. Para as oportunidades mais relevantes, o Claude utiliza `detalhar_vaga` para consultar a descrição completa.
5. Com base no perfil informado, o Claude atribui uma pontuação de compatibilidade e explica os motivos da avaliação.

---

## Funcionalidades

- Busca de vagas em múltiplas plataformas.
- Agregação de resultados em uma estrutura padronizada, sem duplicatas.
- Consulta de detalhes e descrições completas das oportunidades.
- Suporte a buscas por cargo, localização e vagas remotas.
- Análise de compatibilidade entre currículo e requisitos da vaga.
- Pontuação personalizada de acordo com os critérios definidos pelo usuário.
- Dois modos de execução: local (no seu computador) ou online (na nuvem).

---

## Ferramentas MCP

O servidor disponibiliza duas ferramentas:

| Ferramenta | Descrição |
|---|---|
| `buscar_vagas(cargo, local, incluir_remotas, limite_por_fonte)` | Consulta as fontes disponíveis e retorna uma lista unificada de oportunidades. |
| `detalhar_vaga(id)` | Retorna os detalhes e a descrição completa de uma vaga previamente encontrada. |

---

## Exemplo de uso

Após conectar o servidor ao Claude (em qualquer um dos modos), você pode utilizar um prompt como:

> Meu perfil profissional: [cole seu currículo ou resumo].
>
> Busque vagas de Analista de Infraestrutura Júnior em São Paulo.
>
> Considere também oportunidades remotas. Leia as descrições completas das vagas mais promissoras e avalie a compatibilidade com meu perfil de 0 a 100, considerando:
>
> - Habilidades obrigatórias: 40 pontos
> - Senioridade: 20 pontos
> - Habilidades desejáveis: 15 pontos
> - Localização e modalidade: 15 pontos
> - Salário e preferências: 10 pontos
>
> Mostre apenas vagas com pontuação igual ou superior a 80, incluindo o motivo da avaliação.

Os critérios e pesos são definidos diretamente no prompt, permitindo adaptar a análise às prioridades de cada candidatura.

---

## Dois modos de uso: local ou online

O mesmo `server.py` funciona nos dois modos. O que muda é como o Claude se comunica com ele.

| | Modo local | Modo online |
|---|---|---|
| Como funciona | O Claude Desktop inicia o programa no seu computador (transporte `stdio`) | O servidor fica publicado na internet (transporte Streamable HTTP, endpoint `/mcp`) |
| Onde roda | No seu PC | Em uma hospedagem (Render, Cloud Run, Fly.io...) |
| Onde funciona | Apenas no app Claude Desktop | Site, app desktop e celular |
| Hospedagem | Não precisa | Necessária |
| Token (`AUTH_TOKEN`) | Não precisa | Recomendado (obrigatório na prática) |
| Chaves das APIs | No arquivo de configuração do Claude Desktop | Variáveis de ambiente da hospedagem |
| Ideal para | Testar, desenvolver, uso pessoal sem custo de hospedagem | Usar de qualquer dispositivo, sem deixar o PC ligado |

> **Dica:** não deixe os dois conectores ligados ao mesmo tempo no Claude. As ferramentas ficam duplicadas e o assistente pode se confundir. Ative um por vez.

---

## Configuração das APIs

| Fonte | Como obter |
|---|---|
| Adzuna | [developer.adzuna.com](https://developer.adzuna.com/) — `app_id` e `app_key` |
| Jooble | [jooble.org/api/about](https://jooble.org/api/about) — chave de API |
| Remotive | Não exige chave de API |

APIs sem credenciais configuradas são ignoradas automaticamente, e o retorno de `buscar_vagas` traz um aviso informando quais fontes foram puladas.

> Contas novas na Adzuna podem começar com um limite pequeno de chamadas de teste. Cada busca consome uma chamada. Confira o seu plano no painel da Adzuna.

---

## Instalação

### Pré-requisitos

- Python 3.11 ou superior
- Git
- Node.js e npm (apenas para usar o MCP Inspector)
- Credenciais das APIs que deseja habilitar

### Passo a passo

Clone o repositório:

```bash
git clone https://github.com/MariaAndrade-25/vagas-mcp.git
cd vagas-mcp
```

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
```

No Linux ou macOS:

```bash
source .venv/bin/activate
```

No Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

> O projeto usa a API `FastMCP` da versão 1 do SDK. O `requirements.txt` fixa `mcp>=1.9,<2` para evitar o erro `No module named 'mcp.server.fastmcp'` que ocorre com a versão 2.

---

## Modo local (Claude Desktop)

Neste modo o Claude Desktop inicia o `server.py` diretamente, sem servidor HTTP, sem hospedagem e sem token.

### 1. Abra o arquivo de configuração do Claude Desktop

No app, vá em **Settings → Developer → Edit Config**. Se a opção **Developer** não aparecer, ative o modo desenvolvedor em **Help → Troubleshooting → Enable Developer Mode**.

> **Importante (Windows):** dependendo de como o app foi instalado, o arquivo `claude_desktop_config.json` pode estar em mais de uma pasta. O correto é o que o botão **Edit Config** abre. Em algumas instalações ele fica em `%LOCALAPPDATA%\Claude-Data\<pasta-do-app>\claude_desktop_config.json`. Se o arquivo já tiver conteúdo (preferências do app), **não apague nada**: apenas adicione a chave `mcpServers` no mesmo nível das demais.

### 2. Adicione o conector

```json
{
  "mcpServers": {
    "vagas-local": {
      "command": "C:\\caminho\\para\\vagas-mcp\\.venv\\Scripts\\python.exe",
      "args": ["C:\\caminho\\para\\vagas-mcp\\server.py"],
      "env": {
        "MCP_TRANSPORT": "stdio",
        "ADZUNA_APP_ID": "seu-app-id",
        "ADZUNA_APP_KEY": "sua-app-key",
        "ADZUNA_COUNTRY": "br",
        "JOOBLE_KEY": "sua-chave-jooble"
      }
    }
  }
}
```

Observações:

- No Windows, use barras duplas (`\\`) nos caminhos.
- No Linux ou macOS, aponte `command` para `.venv/bin/python` e use caminhos normais.
- A variável `MCP_TRANSPORT=stdio` é o que ativa o modo local. Sem ela, o `server.py` sobe como servidor HTTP.
- `AUTH_TOKEN` não é necessário neste modo, pois o programa não fica exposto na rede.
- `JOOBLE_KEY` é opcional: se não informada, a Jooble é ignorada.

### 3. Reinicie o Claude Desktop

Feche o app por completo (incluindo o ícone da bandeja do sistema) e abra novamente. Depois confira em **Settings → Developer** se o `vagas-local` aparece com status em execução, e procure por ele na lista de ferramentas do chat.

---

## Modo online (servidor HTTP)

Neste modo o servidor roda na nuvem e qualquer dispositivo conectado à sua conta do Claude pode usá-lo.

### 1. Teste localmente antes de publicar

Configure as variáveis de ambiente:

```bash
export AUTH_TOKEN=meu-token
export ADZUNA_APP_ID=...
export ADZUNA_APP_KEY=...
export ADZUNA_COUNTRY=br
export JOOBLE_KEY=...
```

No Windows PowerShell:

```powershell
$env:AUTH_TOKEN="meu-token"
$env:ADZUNA_APP_ID="..."
$env:ADZUNA_APP_KEY="..."
$env:ADZUNA_COUNTRY="br"
$env:JOOBLE_KEY="..."
```

Inicie o servidor:

```bash
python server.py
```

Ele ficará disponível em `http://localhost:8080/mcp`. O endereço `http://localhost:8080/health` responde sem autenticação para checagem de saúde.

> O Claude se conecta pela nuvem, então não consegue acessar `localhost`. Use o servidor local apenas para testes com o MCP Inspector.

### 2. Deploy

O projeto inclui um `Dockerfile` e pode ser hospedado em plataformas que suportam containers, como Render, Fly.io e Google Cloud Run. No Render, este projeto usa deploy contínuo a partir da branch `main`.

Configure as seguintes variáveis de ambiente no painel da plataforma:

```text
AUTH_TOKEN
ADZUNA_APP_ID
ADZUNA_APP_KEY
ADZUNA_COUNTRY
JOOBLE_KEY
```

A variável `ADZUNA_COUNTRY` define o país da busca, por exemplo `br` para Brasil.

Exemplo com Google Cloud Run:

```bash
gcloud run deploy vagas-mcp \
  --source . \
  --region southamerica-east1 \
  --allow-unauthenticated \
  --set-env-vars AUTH_TOKEN=...,ADZUNA_APP_ID=...,ADZUNA_APP_KEY=...,ADZUNA_COUNTRY=br,JOOBLE_KEY=...
```

> **Atenção:** `--allow-unauthenticated` apenas permite que o serviço receba requisições pela rede. O acesso às ferramentas MCP continua protegido pelo token `AUTH_TOKEN`.

Após o deploy, o endpoint será:

```text
https://SEU-SERVICO/mcp
```

Confira se o servidor está no ar abrindo `https://SEU-SERVICO/health`: deve responder `{"ok":true}`. Em planos gratuitos, algumas hospedagens colocam o serviço em repouso quando não há uso, e a primeira chamada pode demorar.

### 3. Conecte ao Claude

No Claude, acesse **Customize → Connectors → Add custom connector** e configure:

| Campo | Valor |
|---|---|
| Nome | Vagas MCP |
| URL | `https://SEU-SERVICO/mcp` |
| Request header | `Authorization` |
| Valor | `Bearer SEU_TOKEN` |

O campo de cabeçalho fica nas configurações avançadas da janela de criação do conector. Após concluir, o Claude poderá utilizar as ferramentas do servidor.

---

## Testando o servidor

### Modo local: verificação rápida via linha de comando

Simula a primeira mensagem que o Claude envia ao conector. No PowerShell:

```powershell
$env:MCP_TRANSPORT="stdio"
'{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"teste","version":"1"}}}' | & ".\.venv\Scripts\python.exe" ".\server.py"
```

Se estiver tudo certo, o programa imprime uma linha de JSON contendo `"serverInfo":{"name":"vagas"...}` e encerra.

> Não digite nada na janela enquanto o servidor estiver rodando em modo `stdio`: ele interpreta tudo o que chega como mensagem MCP e responde com erros de `Invalid JSON`.

### Modo online: MCP Inspector

```bash
npx @modelcontextprotocol/inspector
```

| Configuração | Valor |
|---|---|
| Transporte | Streamable HTTP |
| URL | `http://localhost:8080/mcp` (ou a URL publicada) |
| Authorization | `Bearer meu-token` |

Após conectar, teste `buscar_vagas` e consulte os detalhes de uma vaga com `detalhar_vaga`.

---

## Solução de problemas

| Sintoma | Causa provável | Solução |
|---|---|---|
| `No module named 'mcp.server.fastmcp'` | Instalada a versão 2 do SDK `mcp` | `pip install "mcp<2"` |
| Aviso `adzuna: sem chaves configuradas` | `ADZUNA_APP_ID` ou `ADZUNA_APP_KEY` ausentes ou com o nome errado | Confira os nomes (em maiúsculas, sem espaços) e reinicie o servidor ou o app |
| Aviso `jooble: sem chave configurada` | `JOOBLE_KEY` não definida | Normal se você não usa a Jooble |
| Erros `Invalid JSON` ao rodar com `MCP_TRANSPORT=stdio` | Texto digitado na janela do servidor | Encerre com `Ctrl+C` e use outra janela |
| Conector local não aparece no Claude Desktop | Arquivo de configuração no lugar errado, JSON inválido ou app não reiniciado | Use o botão **Edit Config**, valide o JSON e feche o app por completo |
| `401 não autorizado` no modo online | Token do cabeçalho diferente do `AUTH_TOKEN` do servidor | Use exatamente o mesmo valor, no formato `Bearer <token>` |
| Busca retorna 0 vagas | Fontes sem chave, limite de chamadas esgotado ou termos muito restritos | Veja o campo `avisos` na resposta e amplie os termos da busca |

Para validar o JSON da configuração no PowerShell:

```powershell
Get-Content "CAMINHO\claude_desktop_config.json" -Raw | ConvertFrom-Json
```

---

## Segurança

- Nunca coloque chaves de API ou tokens no código nem em repositórios públicos. Use variáveis de ambiente.
- No modo local, as chaves ficam em texto no `claude_desktop_config.json`: não compartilhe esse arquivo nem imagens dele.
- No modo online, proteja o serviço com um `AUTH_TOKEN` longo e aleatório, e use o mesmo valor no cabeçalho `Authorization` do conector.
- Se uma chave for exposta por engano, gere uma nova no painel da API e atualize todos os lugares onde ela é usada.
- Respeite os termos de uso de cada API.

---

## Destaques técnicos

- Servidor MCP desenvolvido em Python com o SDK oficial.
- Dois transportes no mesmo código: `stdio` (local) e Streamable HTTP, com endpoint `/mcp` (online).
- Integração e normalização de dados provenientes de três APIs, com remoção de duplicatas.
- Autenticação por token utilizando o cabeçalho `Authorization: Bearer`.
- Endpoint `/health` sem autenticação para monitoramento.
- Integração independente com cada fonte: APIs sem credenciais configuradas ou com falha não derrubam a busca; o servidor devolve avisos.
- Containerização com Docker.
- Deploy contínuo no Render a partir da branch `main`.

---

## Tecnologias utilizadas

| Tecnologia | Aplicação |
|---|---|
| Python | Desenvolvimento do servidor e integração com APIs |
| MCP | Exposição das ferramentas para assistentes de IA |
| stdio / Streamable HTTP | Comunicação entre o cliente MCP e o servidor |
| Docker | Containerização da aplicação |
| Render | Hospedagem e deploy contínuo |
| Adzuna, Jooble e Remotive | Fontes de oportunidades de emprego |

---

## Limitações conhecidas

- O cache utilizado por `detalhar_vaga` é armazenado em memória. Após reiniciar o servidor ou utilizar múltiplas instâncias, uma nova busca pode ser necessária antes de consultar os detalhes.
- A disponibilidade, cobertura e qualidade das oportunidades dependem das APIs de terceiros.
- Algumas fontes podem exigir credenciais ou apresentar limites de requisições.
- O modo local funciona apenas no Claude Desktop; para usar no site ou no celular, utilize o modo online.
- A pontuação de compatibilidade é uma avaliação orientativa baseada nos critérios definidos no prompt, não uma garantia de contratação.
- O uso das APIs deve respeitar os respectivos termos de serviço.

---

## Estrutura do projeto

```text
.
├── server.py
├── requirements.txt
├── Dockerfile
└── README.md
```

| Arquivo | Responsabilidade |
|---|---|
| `server.py` | Servidor MCP e integração com as APIs |
| `requirements.txt` | Dependências Python |
| `Dockerfile` | Configuração da imagem Docker |
| `README.md` | Documentação do projeto |

---

## Autora

**Maria Andrade**

Estudante de Análise e Desenvolvimento de Sistemas na 42 São Paulo.

[GitHub](https://github.com/MariaAndrade-25)
