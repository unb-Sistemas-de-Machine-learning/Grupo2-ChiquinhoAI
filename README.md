<center>

# Tópicos Especiais de Engenharia de Software - Bot da UnB

</center>

> Professor: Carla Silva Rocha Aguiar    
> Semestre: 2025.2    
> Tema: API de consulta acadêmica para a Universidade de Brasília (UnB)

<center>

## Integrantes

</center>

<div style="margin: 0 auto; width: fit-content;">

| Nome                                            | Matrícula | Nome de usuário     |
|-------------------------------------------------|-----------|---------------------|
| [Cássio Reis](https://github.com/csreis72)      | 221021886 | csreis72            |
| [João Carvalho](https://github.com/i-JSS)       | 221008150 | i-JSS               |
| [Pablo Serra](https://github.com/Pabloserrapxx) | 221008679 | Pabloserrapxx       |
| [Vinicius Santos](ViniciussdeOliveira)          | 202017263 | ViniciussdeOliveira |

</div>

---

<center>

## Introdução

</center>


Página para o trabalho da disciplina Tópicos Especiais de Engenharia de Software com a professora Carla Silva Rocha Aguiar desenvolvido por alunos da UnB - FGA durante o semestre 25.2. O trabalho consiste na criação de artefatos para a elicitação, análise e modelagem de requisitos e implementação de uma API de consulta acadêmica para a Universidade de Brasília (UnB) usando tecnicas de machine learning e processamento de linguagem natural.


---

<center>

## Pré-requisitos

</center>

Antes de rodar a aplicação, certifique-se de ter instalado:

- **Docker** (versão 20.10 ou superior)
- **Docker Compose** (versão 2.0 ou superior)
- **Make** (opcional, mas recomendado)

---

<center>

## Configuração

</center>

### 1. Configurar variáveis de ambiente

A aplicação requer algumas variáveis de ambiente para funcionar corretamente. Siga os passos abaixo:

#### Arquivo `.env` (raiz do projeto)

O arquivo `.env` na raiz do projeto já está configurado com as portas padrão:

```env
QDRANT_PORT=6333
CLIENT_PORT=8080
SERVER_PORT=55555
SCRAPER_PORT=44444
TELEGRAM_PORT=8443
```

#### Arquivo `server/.env`

Copie o arquivo de exemplo e configure sua chave da API do Google Gemini:

```bash
cp server/.env.example server/.env
```

Em seguida, edite o arquivo `server/.env` e adicione sua chave da API do Google:

```env
GOOGLE_API_KEY=sua_chave_api_aqui
GEMINI_MODEL_NAME=gemini-flash-latest
QDRANT_URL=http://localhost:6333
DEBUG=True
```

**Importante:** Para obter uma chave da API do Google Gemini, acesse [Google AI Studio](https://makersuite.google.com/app/apikey).

#### Arquivo `telegram_bot/.env` (opcional)

Se você deseja usar o bot do Telegram, configure o token:

```bash
cp telegram_bot/.env.example telegram_bot/.env
```

Edite o arquivo `telegram_bot/.env`:

```env
TELEGRAM_BOT_TOKEN=seu_token_aqui
API_URL=http://server:55555/response
```

---

<center>

## Como Rodar a Aplicação

</center>

### Opção 1: Usando Make (Recomendado)

#### Iniciar a aplicação

```bash
make up
```

Este comando irá:
- Construir todas as imagens Docker
- Iniciar todos os serviços (Qdrant, Server, WebScraper, Client e Telegram Bot)
- Inicializar o banco de dados vetorial Qdrant

#### Parar a aplicação

```bash
make down
```

#### Limpar e reconstruir tudo do zero

```bash
make clean
```

Este comando remove todos os containers, volumes e imagens, e reconstrói tudo do zero.

### Opção 2: Usando Docker Compose diretamente

#### Iniciar a aplicação

```bash
docker compose up --build
```

#### Parar a aplicação

```bash
docker compose down
```

#### Limpar volumes e reconstruir

```bash
docker compose down -v --remove-orphans
docker system prune -a --volumes
docker compose build --no-cache
docker compose up
```

---

<center>

## Acessando a Aplicação

</center>

Após iniciar a aplicação, você pode acessá-la através dos seguintes endpoints:

- **Interface Web (Client):** [http://localhost:8080](http://localhost:8080)
- **API Server:** [http://localhost:55555](http://localhost:55555)
- **WebScraper:** [http://localhost:44444](http://localhost:44444)
- **Qdrant Dashboard:** [http://localhost:6333/dashboard](http://localhost:6333/dashboard)
- **Telegram Bot:** Configurado na porta 8443 (se configurado)

---

<center>

## Arquitetura da Aplicação

</center>

A aplicação é composta por 5 serviços principais:

1. **Qdrant:** Banco de dados vetorial para armazenamento de embeddings
2. **Server:** API FastAPI que processa consultas usando RAG (Retrieval-Augmented Generation) com Google Gemini
3. **WebScraper:** Serviço que coleta dados acadêmicos da UnB
4. **Client:** Interface web para interação com o usuário
5. **Telegram Bot:** Bot do Telegram para acesso via mensageiro (opcional)

---

<center>
  
## Deploy do Modelo

</center>

O deploy da aplicação foi realizado na plataforma Railway e está disponível publicamente em: https://chiquinho-ai.up.railway.app/

### Configuração no Railway

Antes de tudo, é possível arrastar o arquivo `docker-compose.prod.yml` diretamente no canvas do Railway para importar os serviços. Em seguida, para cada serviço da aplicação, é necessário:
- Importar o projeto do GitHub no Railway.
- Selecionar o Dockerfile correto (Frontend: Dockerfile.prod; Backend, WebScraper e Telegram Bot: Dockerfile padrão)
- Definir o root directory de cada serviço, pois o projeto é um monorepo
- Configurar as variáveis de ambiente necessárias (ex.: chave da API, URLs internas, tokens)

Por fim, defina o domínio e habilite o public networking apenas para o client (Frontend), enquanto os serviços internos se comunicam entre si pelas URLs internas.

---

<center>

## Histórico de Versão

</center>

<div style="margin: 0 auto; width: fit-content;">

| Data       | Versão | Descrição            | Autores                                   |
|------------|--------|----------------------|-------------------------------------------|
| 20/09/2025 | `1.0`  | Criação do documento | [João Carvalho](https://github.com/i-JSS) |
| 09/12/2025 | `2.0`  | Adição do guia de configuração | [Vinicius Santos](https://github.com/ViniciussdeOliveira) |

</div>
