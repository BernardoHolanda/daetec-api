# daetec-api

Backend do **DAETEC** — sistema de registro de vendas do diretório acadêmico:
produtos, vendas à vista e **fiado**, contas de clientes e **relatório diário** de
fechamento de caixa.

**Stack:** Python · FastAPI · SQLAlchemy · Alembic · PostgreSQL · Docker.

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

A API sobe em **http://localhost:8000**.
Documentação interativa (Swagger) em **http://localhost:8000/docs**.

> Alternativa: o projeto tem um **Dev Container** (`.devcontainer/`) — abra a pasta no
> VS Code e escolha *Reopen in Container* para um ambiente já configurado. Dentro do
> container você já está no serviço `api`, então rode os comandos direto (`alembic
> upgrade head`, `python seed.py`) — sem o prefixo `docker compose exec api`.

### Variáveis de ambiente (`.env`)

| Variável | Descrição |
|---|---|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Credenciais do Postgres |
| `DATABASE_URL` | URL de conexão do SQLAlchemy |
| `JWT_SECRET` | Segredo para assinar os tokens JWT |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` / `ADMIN_EMAIL` | Admin criado pelo `seed.py` |
| `CORS_ORIGINS` | Origens liberadas no CORS (ex.: `http://localhost:5173`) |

> O `.env` real fica **fora do git** (`.gitignore`). Use o `.env.dev` como modelo

## Testes e qualidade de código

**52 testes** em **pytest**, rodando contra um banco Postgres de teste (`daetec_test`) com
isolamento por transação (rollback a cada teste). Rodam também no **GitHub Actions** a cada
push (`.github/workflows/ci.yml`), com o Postgres subindo como *service container*. Lint e
formatação usam **Ruff** (config em `ruff.toml`).

```bash
# dentro do container
pip install --user -r requirements-dev.txt

python -m pytest -v          # testes
python -m ruff check         # lint (imports não usados, ordem, etc.)
python -m ruff format        # formatação automática
```

No VS Code, com a extensão do Ruff instalada (já listada no `devcontainer.json`), a
formatação roda ao salvar.

## Estrutura

```
app/
  main.py          # instância FastAPI, CORS, handler global de 409
  database.py      # engine, sessão, Base
  security.py      # hash de senha (bcrypt) e JWT
  enums.py         # PapelUsuario, FormaPagamento
  models/          # tabelas SQLAlchemy
  schemas/         # modelos Pydantic (entrada/saída)
  crud/            # regras de negócio / acesso a dados
  routers/         # endpoints (auth, produtos, vendedores, clientes, vendas, relatorio, usuarios)
alembic/           # migrations
tests/             # suíte pytest
seed.py            # cria o admin inicial
```
