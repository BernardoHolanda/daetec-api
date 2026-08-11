# daetec-api

[![CI](https://github.com/BernardoHolanda/daetec-api/actions/workflows/ci.yml/badge.svg)](https://github.com/BernardoHolanda/daetec-api/actions/workflows/ci.yml)
[![Backup](https://github.com/BernardoHolanda/daetec-api/actions/workflows/backup.yml/badge.svg)](https://github.com/BernardoHolanda/daetec-api/actions/workflows/backup.yml)

Backend do **DAETEC** — sistema de registro de vendas do diretório acadêmico:
produtos, vendas à vista e **fiado**, contas de clientes e **relatório diário** de
fechamento de caixa.

**Stack:** Python 3.13 · FastAPI · SQLAlchemy 2 · Alembic · PostgreSQL 17 · Docker.

**Frontend:** [BernardoHolanda/daetec-frontend](https://github.com/BernardoHolanda/daetec-frontend) (Vue 3 + TypeScript + Tailwind).

**Em produção:** API no Google Cloud Run, banco no Neon, interface no Cloudflare Pages.

---

## Funcionalidades

- **Autenticação** por JWT com dois papéis: `admin` e `comum`.
- **Produtos, vendedores e clientes** (CRUD, nomes normalizados em MAIÚSCULA, nomes únicos).
  A remoção é barrada pela **chave estrangeira** quando o cadastro já tem histórico —
  quem vendeu, comprou ou é dono de produto não sai (409).
- **Estoque opcional** por produto: `NULL` = não controlado (vende à vontade), `0` =
  esgotado. A venda dá baixa, o cancelamento devolve, e um **CHECK `estoque >= 0`** no
  banco impede que duas vendas simultâneas levem o mesmo último item.
- **Vendas** à vista (com forma de pagamento) ou **fiado** (lançadas na conta do cliente),
  registrando quem fez o lançamento. Cancelamento é **soft delete** (`cancelada_em`) e
  idempotente.
- **Contas** — acompanha o fiado em aberto por cliente e permite fechar a conta.
- **Relatório de fim de dia** — total recebido por vendedor e por forma de pagamento,
  contas em aberto e devedores, agregado no banco (fuso de Manaus, UTC−4).
- Regras de negócio blindadas: validação de formato (422), regra de negócio (400),
  permissão (403) e conflito de duplicidade (409).

## Endpoints

Tudo exige token, exceto `POST /login` e as duas rotas de saúde. O token vai no cabeçalho
`Authorization: Bearer <token>` e vale 60 minutos.

| Método | Rota | Acesso |
|---|---|---|
| `GET` | `/` · `/health/db` | público |
| `POST` | `/login` | público |
| `GET` | `/usuarios/me` | autenticado |
| `POST` `GET` | `/usuarios` · `/usuarios/{id}` | **admin** |
| `GET` | `/produtos` · `/produtos/{id}` | autenticado |
| `POST` `PUT` `DELETE` | `/produtos` · `/produtos/{id}` | **admin** |
| `GET` | `/vendedores` · `/vendedores/{id}` | autenticado |
| `POST` `PUT` `DELETE` | `/vendedores` · `/vendedores/{id}` | **admin** |
| `POST` `GET` | `/clientes` · `/clientes/{id}` | autenticado |
| `PUT` `DELETE` | `/clientes/{id}` | **admin** |
| `GET` | `/clientes/{id}/conta` | autenticado |
| `POST` | `/clientes/{id}/conta/fechar` | autenticado |
| `GET` | `/contas` | autenticado |
| `POST` `GET` | `/vendas` · `/vendas/{id}` | autenticado |
| `DELETE` | `/vendas/{id}` | **admin** |
| `GET` | `/relatorio` | **admin** |

Referência completa e interativa em **`/docs`** (Swagger), gerada a partir dos schemas
Pydantic.

## Como rodar

Requer **Docker** e **Docker Compose**.

```bash
# 1. Crie o arquivo de ambiente a partir do exemplo e ajuste os segredos
cp .env.dev .env

# 2. Suba a API + o banco
docker compose up --build

# 3. Aplique as migrations (em outro terminal)
docker compose exec api alembic upgrade head

# 4. Crie o usuário admin inicial (idempotente)
docker compose exec api python seed.py
```

A API sobe em **http://localhost:8000**, com Swagger em **http://localhost:8000/docs**.

> Alternativa: o projeto tem um **Dev Container** (`.devcontainer/`) — abra a pasta no
> VS Code e escolha *Reopen in Container*. Dentro dele você já está no serviço `api`,
> então rode os comandos direto (`alembic upgrade head`, `python seed.py`) — sem o
> prefixo `docker compose exec api`.

### Variáveis de ambiente (`.env`)

| Variável | Descrição |
|---|---|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Credenciais do Postgres local |
| `DATABASE_URL` | Conexão do SQLAlchemy (dialeto `postgresql+psycopg`) |
| `JWT_SECRET` | Segredo que assina os tokens |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` / `ADMIN_EMAIL` | Admin criado pelo `seed.py` |
| `CORS_ORIGINS` | Origens liberadas, separadas por vírgula |
| `DATABASE_URL_NUVEM` | *(opcional)* conexão com a produção no Neon |
| `DATABASE_URL_HOMOLOG` | *(opcional)* conexão com o branch `homolog`; exigida pelo `homolog.sh` |

`DATABASE_URL` e `JWT_SECRET` são lidos com `os.environ[...]`, não com `os.getenv()`: sem
eles o processo **morre no boot**, em vez de subir e quebrar na primeira requisição que
precisar do valor.

> O `.env` real fica **fora do git** (`.gitignore`). Use o `.env.dev` como modelo.

## Testes e qualidade de código

**52 testes** em **pytest**, contra um Postgres de teste (`daetec_test`) com isolamento por
transação — cada teste roda dentro de uma transação desfeita no fim, então a ordem dos
testes nunca importa. Rodam também no **GitHub Actions** a cada push, com o Postgres
subindo como *service container*. Lint e formatação com **Ruff** (`ruff.toml`).

```bash
# dentro do container
pip install --user -r requirements-dev.txt

python -m pytest -v          # testes
python -m ruff check         # lint
python -m ruff format        # formatação
```

## Dependências

Duas camadas, de propósito:

- **`requirements.in`** — as dependências que o projeto escolheu, sem versão. É o que se
  edita.
- **`requirements.txt`** — **gerado**, com todas as versões travadas em `==`, incluindo as
  transitivas. É o que se instala. Sem isso um build futuro puxa versão nova de algo que
  você nem sabe que usa e quebra sem ninguém ter mexido no código.

O comando para regenerar está no cabeçalho do próprio `requirements.txt`.

## Migrations

Alembic, com `autogenerate` a partir dos modelos.

```bash
docker compose exec api alembic revision --autogenerate -m "descrição"
docker compose exec api alembic upgrade head
docker compose exec api alembic current      # em que revisão o banco está
```

Sempre **leia o arquivo gerado** antes de aplicar: o `autogenerate` compara modelos com o
banco e às vezes propõe mudanças que você não pediu — inclusive apagar índices, se os
modelos estiverem defasados em relação ao banco.

## Ambientes

| Ambiente | Banco | Para quê |
|---|---|---|
| **local** | Postgres no Docker | ciclo rápido, dados descartáveis, testes |
| **homolog** | branch `homolog` no Neon | ensaiar operação arriscada com dados reais |
| **produção** | branch `production` no Neon | vale |

Homologação não substitui o local — ela fica **entre** o local e a produção. O local é 18×
mais rápido (conexão local contra ida e volta até São Paulo), e a suíte de testes começa
com `drop_all`, que jamais deve apontar para a nuvem.

Para rodar qualquer comando contra o homolog, use o atalho — ele anuncia o host antes de
executar, justamente para você não confundir os bancos:

```bash
./homolog.sh alembic upgrade head
./homolog.sh python seed.py
```

## Deploy

A imagem é **multi-stage**: o estágio `dev` tem git (o Dev Container precisa), e o
`producao` não — são 136 MB a menos viajando em cada deploy. `producao` é o **último**
estágio do Dockerfile, que é o alvo padrão do build, então o Cloud Run constrói o certo sem
receber nenhum parâmetro.

Depois de um deploy, **confira em qual revisão está o tráfego**: revisão que falha ao subir
fica com 0% e a anterior continua servindo — o push "funciona" e o comportamento não muda,
porque o código novo nunca atendeu ninguém.

## Backup

`.github/workflows/backup.yml` roda `pg_dump` contra a produção **todo domingo às 06:00**
(Manaus) e guarda o resultado como artefato por 90 dias. Também dá para disparar na mão
pelo botão *Run workflow*.

O job **falha de propósito** se o dump sair com menos de 1 KB: `pg_dump` malsucedido pode
gerar arquivo vazio e terminar com status 0, e backup que ninguém confere não é backup.

> Workflow agendado é desativado pelo GitHub após 60 dias sem atividade no repositório.

## Estrutura

```
app/
  main.py          # instância FastAPI, CORS, handler global de 409
  database.py      # engine, sessão, Base
  security.py      # hash de senha (bcrypt) e JWT
  dependencies.py  # get_current_user, exigir_admin
  enums.py         # PapelUsuario, FormaPagamento
  models/          # tabelas SQLAlchemy
  schemas/         # modelos Pydantic (entrada/saída)
  crud/            # regras de negócio / acesso a dados
  routers/         # endpoints
alembic/           # migrations
tests/             # suíte pytest
.github/workflows/ # ci.yml (testes) e backup.yml (pg_dump semanal)
seed.py            # cria o admin inicial
homolog.sh         # roda comandos contra o branch de homologação
```
