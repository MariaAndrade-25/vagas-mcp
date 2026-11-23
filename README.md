# Vagas MCP
<p align="center">

<img width="346" height="260" alt="WorkHeresGIF" src="https://github.com/user-attachments/assets/9cea1029-1614-4538-bd16-0bd7e4235292" />
</p>


**Um conector MCP para buscar, centralizar e analisar vagas de emprego em diferentes plataformas.**

O Vagas MCP reúne oportunidades de emprego de **Adzuna, Jooble e Remotive** em um único lugar, permitindo que assistentes de IA como o Claude pesquisem vagas, consultem descrições completas e avaliem a compatibilidade com o perfil profissional do usuário.

A proposta é simplificar a busca por oportunidades: em vez de acessar vários sites e comparar cada vaga manualmente, você informa seu currículo, define os critérios desejados e recebe uma seleção de oportunidades alinhadas aos seus objetivos profissionais.

---

## Como funciona

```text
                         ┌──────────────┐
                         │    Claude   │
                         └──────┬───────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │    Vagas MCP       │
                    │  Streamable HTTP   │
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
3. O servidor agrega e normaliza os resultados em um formato único.
4. Para as oportunidades mais relevantes, o Claude utiliza `detalhar_vaga` para consultar a descrição completa.
5. Com base no perfil informado, o Claude atribui uma pontuação de compatibilidade e explica os motivos da avaliação.

---

## Funcionalidades

- Busca de vagas em múltiplas plataformas.
- Agregação de resultados em uma estrutura padronizada.
- Consulta de detalhes e descrições completas das oportunidades.
- Suporte a buscas por cargo, localização e vagas remotas.
- Análise de compatibilidade entre currículo e requisitos da vaga.
- Pontuação personalizada de acordo com os critérios definidos pelo usuário.

---

## Ferramentas MCP

O servidor disponibiliza duas ferramentas:

| Ferramenta | Descrição |
|---|---|
| `buscar_vagas(cargo, local, incluir_remotas, limite_por_fonte)` | Consulta as fontes disponíveis e retorna uma lista unificada de oportunidades. |
| `detalhar_vaga(id)` | Retorna os detalhes e a descrição completa de uma vaga previamente encontrada. |

---

## Exemplo de uso

Após conectar o servidor ao Claude, você pode utilizar um prompt como:

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

## Destaques técnicos

- Servidor MCP desenvolvido em Python.
- Comunicação via **Streamable HTTP**, com endpoint `/mcp`.
- Integração e normalização de dados provenientes de três APIs.
- Autenticação por token utilizando o cabeçalho `Authorization: Bearer`.
- Endpoint `/health` sem autenticação para monitoramento.
- Integração independente com cada fonte: APIs sem credenciais configuradas são ignoradas automaticamente.
- Containerização com Docker.
- Deploy contínuo no Render a partir da branch `main`.

---

## Tecnologias utilizadas

| Tecnologia | Aplicação |
|---|---|
| Python | Desenvolvimento do servidor e integração com APIs |
| MCP | Exposição das ferramentas para assistentes de IA |
| Streamable HTTP | Comunicação entre o cliente MCP e o servidor |
| Docker | Containerização da aplicação |
| Render | Hospedagem e deploy contínuo |
| Adzuna, Jooble e Remotive | Fontes de oportunidades de emprego |

---

## Executando localmente

### 1. Pré-requisitos

- Python instalado
- Git
- Node.js e npm, para utilizar o MCP Inspector
- Credenciais das APIs que deseja habilitar

### 2. Configuração das APIs

| Fonte | Como obter |
|---|---|
| Adzuna | [developer.adzuna.com](https://developer.adzuna.com/) — `app_id` e `app_key` |
| Jooble | [jooble.org/api/about](https://jooble.org/api/about) — chave de API |
| Remotive | Não exige chave de API |

### 3. Instalação

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

### 4. Variáveis de ambiente

Configure as credenciais necessárias:

```bash
export AUTH_TOKEN=meu-token
export ADZUNA_APP_ID=...
export ADZUNA_APP_KEY=...
export JOOBLE_KEY=...
```

No Windows PowerShell, utilize:

```powershell
$env:AUTH_TOKEN="meu-token"
$env:ADZUNA_APP_ID="..."
$env:ADZUNA_APP_KEY="..."
$env:JOOBLE_KEY="..."
```

### 5. Inicie o servidor

```bash
python server.py
```

O servidor estará disponível localmente em:

```text
http://localhost:8080/mcp
```

---

## Testando com o MCP Inspector

O MCP Inspector permite testar as ferramentas do servidor e verificar a comunicação MCP.

Execute:

```bash
npx @modelcontextprotocol/inspector
```

Configure a conexão com os seguintes parâmetros:

| Configuração | Valor |
|---|---|
| Transporte | Streamable HTTP |
| URL | `http://localhost:8080/mcp` |
| Authorization | `Bearer meu-token` |

Após conectar, teste a ferramenta `buscar_vagas` e consulte os detalhes de uma oportunidade utilizando `detalhar_vaga`.

---

## Deploy

O projeto inclui um `Dockerfile` e pode ser hospedado em plataformas que suportam containers, como:

- Render
- Fly.io
- Google Cloud Run

### Variáveis de ambiente

Configure as seguintes variáveis no painel da plataforma:

```text
AUTH_TOKEN
ADZUNA_APP_ID
ADZUNA_APP_KEY
ADZUNA_COUNTRY
JOOBLE_KEY
```

A variável `ADZUNA_COUNTRY` permite definir o país da busca, por exemplo, `br` para Brasil.

### Exemplo: Google Cloud Run

```bash
gcloud run deploy vagas-mcp \
  --source . \
  --region southamerica-east1 \
  --allow-unauthenticated \
  --set-env-vars AUTH_TOKEN=...,ADZUNA_APP_ID=...,ADZUNA_APP_KEY=...,ADZUNA_COUNTRY=br,JOOBLE_KEY=...
```

> **Atenção:** `--allow-unauthenticated` permite que o serviço receba requisições pela rede. O acesso às ferramentas MCP continua protegido pelo token `AUTH_TOKEN`.

Após o deploy, o endpoint do servidor será:

```text
https://SEU-SERVICO/mcp
```

---

## Conectando ao Claude

No Claude, acesse:

**Customize → Connectors → Add custom connector**

Configure a conexão:

| Campo | Valor |
|---|---|
| Nome | Vagas MCP |
| URL | `https://SEU-SERVICO/mcp` |
| Request header | `Authorization` |
| Valor | `Bearer SEU_TOKEN` |

Após concluir a configuração, o Claude poderá utilizar as ferramentas do servidor para buscar e consultar oportunidades.

---

## Limitações conhecidas

- O cache utilizado por `detalhar_vaga` é armazenado em memória. Após reiniciar o servidor ou utilizar múltiplas instâncias, uma nova busca pode ser necessária antes de consultar os detalhes.
- A disponibilidade, cobertura e qualidade das oportunidades dependem das APIs de terceiros.
- Algumas fontes podem exigir credenciais ou apresentar limites de requisições.
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
