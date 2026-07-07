# DAETEC API — Diário de Bordo

> Registro do aprendizado e do estado do projeto (backend).
> Para o **o quê/porquê** do produto, veja `../DEFINICAO.md`.
> Última atualização: 2026-07-07

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Linguagem | Python 3.13 |
| Framework | FastAPI |
| Validação | Pydantic |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Banco | PostgreSQL 17 |
| Infra | Docker + Docker Compose |
| Dev | Dev Containers (VS Code) |

Arquitetura em **camadas** dentro de `app/`:
`models/` (tabelas) → `schemas/` (contrato Pydantic) → `crud/` (acesso ao banco)
→ `routers/` (endpoints) → `main.py` (junta tudo).

## Como rodar

```bash
# subir tudo (api + banco) em segundo plano
docker compose up -d

# ver logs da api
docker compose logs -f api

# parar
docker compose down
```

- API: http://localhost:8000
- Documentação interativa: http://localhost:8000/docs
- Saúde do banco: http://localhost:8000/health/db

No **VS Code**: `Ctrl+Shift+P` → "Dev Containers: Reopen in Container" para
editar de dentro do container (com autocomplete). Lá o terminal já está dentro,
então comandos dispensam o prefixo `docker compose exec api`.

## Estado atual

- ✅ Fundação completa: Docker, Postgres, FastAPI, Alembic, Dev Container.
- ✅ Arquitetura em camadas montada (`app/`).
- ✅ Recurso **produtos** com CRUD completo (criar, listar, obter, atualizar, deletar).
- ✅ Recurso **vendedores** (criar, listar, obter, atualizar).
  `deletar` **adiado de propósito**: apagar vendedor com `ItemVenda` viola a FK
  (`IntegrityError`) — vira lição própria de foreign key depois que houver vendas.
- ✅ Domínio de vendas modelado: `Venda` → `ItemVenda` (N) → `Produto`/`Vendedor`.
  **Vendedor é por item** (uma venda pode ter produtos de vários vendedores) e o
  `preco_unitario` fica **congelado** no item (histórico de preço).
- ✅ Recurso **vendas**: `criar` (registrar, congela preço), `listar`, `obter`.
  **Sem `atualizar`** de propósito — venda é registro imutável (evento), não cadastro.
- 🔜 Próximo (lição 18): **cancelamento de venda** (soft delete, campo `cancelada_em`)
  + **foreign key / cascade** — apagar/cancelar lida com os `itens_venda` dependentes.
  Depois: `forma_pagamento`, a **conta** (fiado) e o **relatório**. Mais à frente:
  testes (pytest), auth (JWT), frontend (Vue).

### Modelo de dados atual

```
Vendedor ─1:N─ ItemVenda ─N:1─ Produto
                   │
Venda ────1:N──────┘   (ItemVenda: quantidade, preco_unitario congelado)
```

## Comandos úteis

```bash
# --- Alembic (migrations) ---
docker compose exec api alembic revision --autogenerate -m "descricao"  # gerar
docker compose exec api alembic upgrade head                            # aplicar
docker compose exec api alembic downgrade -1                            # desfazer 1

# --- Banco (psql) ---
docker compose exec db psql -U daetec -d daetec -c "\dt"          # listar tabelas
docker compose exec db psql -U daetec -d daetec -c "\d produtos"  # ver colunas

# --- Rebuild (quando mudar Dockerfile ou requirements.txt) ---
docker compose up -d --build
```

> 📌 Regra de ouro: **mudou código** → o hot reload cuida sozinho.
> **Mudou dependência ou Dockerfile** → precisa `--build`.

## Lições concluídas

| # | Tema | O que ficou de aprendizado |
|---|------|----------------------------|
| 1 | Git — início | `git init`, branch `main`, identidade **por repositório** (e-mail pessoal local x trabalho global). |
| 2 | Primeiro commit | As 3 áreas (working / staging / repository), ciclo `add → commit`, `.gitignore`. |
| 3 | API mínima | FastAPI "olá mundo", `requirements.txt`, decisão Docker-first (sem venv). |
| 4 | Dockerfile | Imagem × container, `build`, `run`, mapeamento de portas, cache de camadas. |
| 5 | Compose + volumes | `docker compose`, bind mount e **hot reload**. |
| 6 | PostgreSQL | Rede entre serviços (host = nome do serviço), volume nomeado (persistência), `-d`. |
| 7 | Conectar ao banco | SQLAlchemy engine/session, segredos no `.env` + `.env.example`, `DATABASE_URL`. |
| 8 | Arquitetura em camadas | Pacote `app/`, `WORKDIR /code`, imports de pacote (`from app...`). |
| 9 | Alembic | `init`, configurar `env.py`, autogenerate, `upgrade head` → tabela `produtos`. |
| 10 | Dev Containers | Editor dentro do container, usuário `appuser` (HOME), instalar `git` na imagem slim. |
| 11 | Endpoints (produtos) | Schemas Pydantic, dependência `get_db`, `crud`, `router`, `include_router`. |
| 12 | CRUD completo | Path params `{id}`, `HTTPException` 404, status 204. |
| 13 | Foreign Key | `ForeignKey(...)`, integridade referencial, `server_default=func.now()`. |
| 14 | `relationship()` | Navegação no ORM (`back_populates`), `TYPE_CHECKING` p/ evitar import circular. |
| 15 | Remodelar venda | `ItemVenda` (vendedor por item, preço congelado), `alembic downgrade -1`. |
| 16 | Endpoints (vendedores) | **Feito por mim**, replicando o padrão de produtos (só `criar`, `listar`; depois `obter`, `atualizar`). |
| 17 | Registrar venda | Schema **aninhado** (`VendaCreate` c/ `list[ItemVendaCreate]`), **transação** (um `commit` = tudo ou nada), **congelar preço** (`preco_unitario` copiado do produto no ato), `venda.itens.append` + *cascade* do `relationship`, e **erro de domínio no crud (`ValueError`) traduzido pra HTTP no router**. Inclui `listar` e `obter`. |

## Lições de depuração (pra levar pra vida)

- **Traceback lê-se de baixo pra cima** — a última linha é a causa real.
- **`func` × `func()`** — sem os parênteses, a função **não é chamada** (bug silencioso,
  sem erro). Ex.: `db.commit` não grava nada; `db.commit()` grava.
- **Imagem `slim`** vem mínima — falta `git`, etc.: instala-se no `Dockerfile` via `apt-get`.
- **Arquivos criados dentro do container** nascem do `root` por padrão — por isso
  rodamos como `appuser` (uid 1000).
- **Copiar-e-adaptar** um arquivo: renomeie **tudo** por dentro (nomes de funções
  etc.), senão dá `AttributeError` só em tempo de execução.
- **`psql` via `docker compose exec`**: use a flag **`-T`** para a saída sair limpa
  (sem `-T` o `\d` pode se perder num paginador e aparecer vazio).
- **Dev Container × `docker compose` no host**: com o Dev Container aberto, **não**
  rode `docker compose up/down/restart` no terminal do host — o VS Code gerencia o
  próprio container do serviço `api` (imagem `vsc-...`), e o `up` da CLI o **recria**
  na versão crua, derrubando a conexão (VS Code trava tentando reconectar). Conserto:
  *Dev Containers: Rebuild and Reopen in Container*. Código Python nem precisa: o
  `fastapi dev` faz **hot reload** sozinho.
