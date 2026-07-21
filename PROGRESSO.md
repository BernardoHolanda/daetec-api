# DAETEC API — Diário de Bordo

> Registro do aprendizado e do estado do projeto (backend).
> Para o **o quê/porquê** do produto, veja `../DEFINICAO.md`.
> Última atualização: 2026-07-21

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

# semear o admin inicial (idempotente; lê ADMIN_* do .env)
docker compose exec api python seed.py
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
- ✅ Recurso **vendas**: `criar` (congela preço, exige `forma_pagamento`),
  `listar` (só ativas), `obter`, `cancelar` (soft delete via `cancelada_em`).
  **Sem `atualizar`** — venda é registro imutável (evento), não cadastro.
- ✅ **`forma_pagamento`** (Enum pix/dinheiro/débito/crédito), validado em duas
  camadas (Pydantic + ENUM nativo do Postgres). **Anulável** desde a lição 20:
  venda fiado ainda não tem forma de pagamento (só se sabe no fechamento).
- ✅ Recurso **clientes** (criar, listar, obter, atualizar) — cadastro igual ao
  vendedor. Sem `deletar` (mesma armadilha de FK).
- ✅ **Conta / fiado** (Opção A: venda "na conta" é só uma venda com dono e ainda
  não paga). `Venda` ganhou `cliente_id` (nullable FK) e `paga_em` (nullable).
  `criar_venda` decide fiado×à vista; `GET /clientes/{id}/conta` é uma **visão
  calculada** (soma das vendas em aberto); `POST /clientes/{id}/conta/fechar`
  quita tudo num **update em lote** (um só `commit`, mesmo `paga_em`).
- ✅ **Relatório de fim de dia** (`GET /relatorio?dia=`): quebra **por vendedor**
  (agrega no nível do `ItemVenda`), com **recebido** (por forma, filtrado por
  `paga_em`) **separado** da **conta em aberto** (por cliente, saldo acumulado,
  sem filtro de data) + seção de **devedores**. Agregação (`SUM`/`GROUP BY`) feita
  no **Postgres**, não no Python. Fiado quitado **migra** de "conta" p/ "recebido"
  no dia do pagamento (provado ao vivo).
- ✅ **Autenticação — base** (lição 22): `Usuario` **independente** (sem vínculo
  com vendedor), com `papel` (Enum admin/comum) → base de **RBAC** (comum vende;
  admin cria/altera/deleta/relatório). Senha **nunca** em texto puro: `senha_hash`
  com **bcrypt** (salt embutido, lento de propósito), em `app/security.py`
  (`hash_senha`/`verificar_senha`). Schema **assimétrico**: `senha` só entra
  (`UsuarioCreate`), nunca sai (`UsuarioRead` sem hash + `response_model` como 2ª
  barreira). `criar_usuario` faz a **ponte** senha→hash.
- ✅ **Login + JWT** (lição 23): `POST /login` (form `OAuth2PasswordRequestForm`)
  confere a senha com `verificar_senha` e emite um **JWT assinado** (`criar_token`
  em `app/security.py`) com `sub`/`papel`/`exp`. Erro **único** ("usuário ou senha
  inválidos") pros dois casos — não entrega quais usernames existem.
- ✅ **Proteção de rotas** (lição 24): dependência `get_current_user` em
  `app/dependencies.py` — lê `Authorization: Bearer` (`OAuth2PasswordBearer`),
  valida assinatura + `exp` (`jwt.decode`) e re-busca o usuário no banco. Token
  inválido/adulterado/vencido → **401**. `GET /usuarios/me` protegido de exemplo.
- ✅ **RBAC / papéis** (lição 25): dependência `exigir_admin` (encadeia em
  `get_current_user`) → **403** pra comum em ação de admin. **401 = quem é você**;
  **403 = sei quem é, mas não pode**. Aplicado por rota (`dependencies=[...]` no
  decorador) ou por router inteiro (relatório). Regra: **comum vende + lê**; **admin
  cria/altera/deleta + relatório**. `POST /clientes` (abrir conta) e fechar conta
  ficam **livres** (fazem parte de vender); `PUT /clientes` é admin (gestão).
- ✅ **Robustez — validação + erros** (lição 26): auditoria de entradas ruins →
  fechados 3 buracos que davam **500 cru**. **Categoria A (borda/Pydantic → 422)**:
  `Field(min_length=1)` nos itens (barra venda vazia) e `Field(gt=0)` na quantidade.
  **Categoria B (domínio/crud → 400)**: validação do **vendedor** no `criar_venda`
  (espelha produto/cliente) e **username duplicado** no `criar_usuario`
  (checar-antes-de-inserir; o `unique` do banco é a rede de segurança, a checagem
  dá o erro bonito). Router traduz `ValueError → 400`.
- ✅ **Timestamps com fuso** (lição 27): colunas de data viraram `timestamptz`
  (`DateTime(timezone=True)`) → API devolve com `Z` (UTC), front converte pro local.
  Migration com `postgresql_using "col AT TIME ZONE 'UTC'"` (os naive já eram UTC).
  O **"dia" do relatório** passou a ser dia de **Manaus** (UTC−4 fixo, sem DST —
  `FUSO_MANAUS`), não dia UTC — senão o corte cairia às 20h local.
- ✅ **Blindagem do banco** (lição 28): o **backend é o dono da integridade, nunca
  o front** (front é burlável). Nomes **normalizados** (`strip().upper()` via um tipo
  reutilizável `Annotated[str, AfterValidator]`) → "batata"="BATATA". `preco` e
  `quantidade` com `Field(gt=0)`. **UNIQUE** em `produto`/`vendedor`/`cliente.nome`
  (migration **à mão** — autogenerate não detecta UNIQUE) + **handler global** de
  `IntegrityError` → **409** (nenhuma violação vaza como 500).
- ✅ **Seed** (`seed.py`): cria o **admin inicial** de forma **idempotente** (resolve
  o ovo-e-galinha — o 1º admin não pode ser criado pela API, que exige admin logado).
  Lê `ADMIN_USERNAME`/`ADMIN_PASSWORD` do `.env` (aborta se a senha faltar). Rodar:
  `docker compose exec api python seed.py`. (As vars do `.env` só entram no container
  após ele ser **recriado** — `env_file` carrega no start.)
- ✅ **Usuário: email + senha forte** (lição 29): `email` **obrigatório/único**
  (`EmailStr`) no `Usuario`; senha validada na entrada (`SenhaForte`: ≥8, ≥1 número,
  ≥1 maiúscula). Seed passou a definir `ADMIN_EMAIL`. Login de teste agora:
  `admin` / `Senhaforte1`.
- 🔜 Próximo: **auditoria** (`registrado_por`/`fechada_por` + trancar rotas de venda);
  depois **testes** (pytest) e frontend (Vue).

### Modelo de dados atual

```
Vendedor ─1:N─ ItemVenda ─N:1─ Produto
                   │
Venda ────1:N──────┘   (ItemVenda: quantidade, preco_unitario congelado)
  │
  └─N:1─ Cliente   (cliente_id nullable: NULL = à vista; preenchido = fiado)
                   (paga_em nullable: NULL = em aberto; data = quitada)

Usuario   (isolado: username único, senha_hash, papel admin/comum)
          (NÃO liga a vendedor — só autenticação/autorização; base do login/RBAC)
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
| 7 | Conectar ao banco | SQLAlchemy engine/session, segredos no `.env` + `.env.dev` (template), `DATABASE_URL`. |
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
| 18 | Cancelar venda (soft delete) + FK | **Integridade referencial** vista ao vivo (`DELETE` cru barrado pela FK). **Soft delete**: coluna nullable `cancelada_em` (migration segura porque nullable), `cancelar_venda` marca a data (não apaga), `listar` esconde canceladas (`.is_(None)`), `obter` mantém p/ auditoria. HTTP: cancelar devolve o recurso (**200 + `VendaRead`**), não 204 — contraste hard×soft delete. |
| 19 | Forma de pagamento (Enum) | **Enum** (`class FormaPagamento(str, Enum)`) = conjunto fixo de valores; fonte única em `app/enums.py` (model + schema importam). Validação automática (valor inválido → 422, com mensagem que lista as opções) **em duas camadas**: Pydantic **e** tipo ENUM nativo do Postgres. Coluna **NOT NULL** obrigou limpar dados de teste antes (add NOT NULL em tabela com linhas falha). |
| 20 | Conta / fiado | Cadastro de **cliente** (exercício solo). **Opção A de modelagem**: venda "na conta" é só uma `Venda` com `cliente_id` (nullable FK) e `paga_em` (nullable) — sem tabela paralela, reaproveita tudo. Requisito novo (fiado) **afrouxou** `forma_pagamento` pra nullable (software evolui). `criar_venda` com **dois caminhos** (fiado × à vista). `GET /clientes/{id}/conta` = **visão calculada** (não mapeia tabela; soma `quantidade × preço` das vendas em aberto; `Decimal("0")` de base). `POST .../conta/fechar` = **update em lote numa transação** (loop + um `commit` = mesmo `paga_em` em todas). Colunas nullable → migration segura mesmo com dados; autogenerate acertou sozinho (`alter_column` afrouxando NOT NULL + FK). |
| 21 | Relatório (agregação) | **Agregação no banco** em vez de somar no Python: `func.sum(a*b)`, `func.coalesce(sum, 0)`, `.join(Venda, ...)`, `.group_by(...)` com 1 e **2 colunas**. O trio **`db.scalar`** (1 valor) × **`db.scalars`** (1 coluna) × **`db.execute(...).all()`** (linhas inteiras). Remontar linhas achatadas em dict aninhado com **`setdefault(k, {})[k2] = v`**. **Recebido** (por `paga_em`, fiado sai sozinho pois `NULL >= x` é falso) **separado** da **conta em aberto** (sem data, saldo acumulado). Montagem: **query param opcional** `?dia=` (3º jeito de receber dado, além de path e body) c/ default `date.today()`, de-para `{id: nome}`, **união de chaves** `set(a) \| set(b)`. Anotação de tipo (`-> Decimal`) é avaliada **no import** — nome indefinido derruba o app. |
| 22 | Auth — senha/hash | `Usuario` **standalone** (sem FK p/ vendedor) + `papel` (Enum admin/comum) = base de **RBAC**. **Hash de senha** com **bcrypt** (`hash_senha`/`verificar_senha` em `app/security.py`): transformação **só de ida**, **salt** embutido no próprio hash (`$2b$12$…`), lento de propósito — igual `password_hash()` do PHP. Schema **assimétrico**: senha entra crua (`UsuarioCreate`), **nunca** sai (`UsuarioRead` sem hash + `response_model` como 2ª barreira). `criar_usuario` é a **ponte** senha→hash. Migration: `create_table` **cria o tipo ENUM sozinho** (≠ `add_column` da lição 19). Dependência nova (`bcrypt`) → **rebuild** do container (via *Dev Containers: Rebuild*). |
| 23 | Login + JWT | **JWT** = `header.payload.signature`; **assinado, não criptografado** (o payload é base64 legível — nada de segredo lá; o que protege é a **assinatura** com `JWT_SECRET`). **Stateless** (servidor não guarda sessão). `criar_token` (`jwt.encode`, HS256, claims `sub`/`papel`/`exp`; PyJWT converte `datetime`→timestamp e valida `exp` sozinho). `POST /login` usa **`OAuth2PasswordRequestForm`** (form-data, não JSON — é o que faz o *Authorize* do `/docs` funcionar depois). **Erro único** pros dois casos (senha errada × user inexistente) → não enumera usernames. `pyjwt` novo → rebuild. |
| 24 | Proteger rotas | Dependência **`get_current_user`** (`app/dependencies.py`): **`OAuth2PasswordBearer`** lê o header `Authorization: Bearer`; `jwt.decode` valida assinatura **e** `exp`; re-busca o usuário no banco (token válido mas user apagado → barra). Erro → **401** (+ `WWW-Authenticate: Bearer`). Usa-se com `Depends(get_current_user)`. **Ordem de rota**: `/me` **antes** de `/{id}` (senão `"me"` cai no parse de int → 422). Reforço do nugget da lição 21: **default de parâmetro é avaliado na definição** — `Depends(get_current_user)` exige a função **acima**. |
| 29 | Email + senha forte | `email` **obrigatório/único** no `Usuario` via **`EmailStr`** (lib `email-validator` → rebuild). Regra de **senha** (`SenhaForte` = `Annotated[str, AfterValidator]`: ≥8, ≥1 dígito, ≥1 maiúscula) só na **entrada** (`UsuarioCreate`). Pegadinhas: (1) `EmailStr` **rejeita `.local`** (domínio reservado) — e o seed grava direto no banco, então email inválido só explode na **leitura** (`ResponseValidationError` 500) → seed tem que usar dado válido; (2) o autogenerate criou a UNIQUE do email **sem nome** → nomear (`uq_usuarios_email`) p/ o downgrade não quebrar; (3) crud `criar_usuario` não passava `email` → `INSERT` com `NULL` → `IntegrityError` mascarado de **409 "já existe"** (handler genérico esconde bug de `NOT NULL`). |
| 28 | Blindar o banco | **Backend é o dono da integridade, nunca o front** (front é burlável). **Normalizar × validar**: dá pra consertar sozinho (caixa/espaços) → **normaliza** (`Annotated[str, AfterValidator(strip+upper)]`, tipo reutilizável); não dá (preço 0, vazio) → **rejeita 422** (`Field(gt=0)`). **UNIQUE** em produto/vendedor/cliente.nome (decisão: todos únicos no contexto pequeno). Pegadinha: **autogenerate NÃO gera constraint UNIQUE** — migration escrita à mão (`drop_index` do índice comum + `create_unique_constraint`). **Handler global** `@app.exception_handler(IntegrityError)` → **409**: rede de segurança única, nenhum 500 vaza. Limpar dados de teste antes (constraint não entra em tabela suja). |
| 27 | Timestamps com fuso | `TIMESTAMP WITHOUT TIME ZONE` **descarta o fuso** → a API devolvia hora "solta" (sem `Z`/offset) e o front poderia errar o dia. Fix: `DateTime(timezone=True)` → `timestamptz` (guarda o **instante absoluto** em UTC e emite o offset). O código já gravava `datetime.now(timezone.utc)` (a parte difícil já estava certa). Migration: o autogenerate detecta o **tipo** mas não a **conversão dos dados** → `postgresql_using="col AT TIME ZONE 'UTC'"` declara que os valores naive eram UTC. Domínio: o **"dia" do relatório** virou dia de **Manaus** (`FUSO_MANAUS`, UTC−4 fixo) via `datetime.combine(dia, ..., tzinfo=...)` — comparar aware×`timestamptz` funciona; naive cairia no fuso da sessão. |
| 26 | Robustez (validação + erros) | **Auditar batendo na API com entradas ruins** — erro que não grita é o pior (venda de itens vazios criava uma venda-fantasma 201). Dois baldes: **A) entrada malformada** → barra no **schema (Pydantic `Field`)** → **422** declarativo (`Field(min_length=1)`, `Field(gt=0)`); **B) erro de domínio** (dado válido que viola regra) → barra no **crud** com `ValueError` → router traduz p/ **400** (validar vendedor; username duplicado via checar-antes-de-inserir). Camadas de defesa: `unique` do banco (garantia) + checagem no código (mensagem bonita). Ressalva: checar-e-inserir tem corrida teórica; à prova de corrida = capturar `IntegrityError`. |
| 25 | RBAC / papéis | **Autenticação × autorização**: **401** = "não sei quem é você"; **403** = "sei, mas você não pode". `exigir_admin` **encadeia** em `get_current_user` e checa `papel` → 403. Aplicação **por rota** (`dependencies=[Depends(exigir_admin)]` no decorador, quando não precisa do usuário) ou **por router inteiro** (relatório). Mapa: comum **vende + lê**; admin **escreve cadastros + relatório + cancela venda**. Refino de domínio: **abrir cliente** e **fechar conta** = livres (é vender); **alterar** cadastro = admin. Critério p/ decidir: *"isso trava uma venda?"*. |

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
- **Enum + Alembic no Postgres**: `op.add_column` com `sa.Enum` **não cria o tipo
  ENUM sozinho** (só `create_table` cria). Falha com *"type X does not exist"*. No
  `upgrade`: `sa.Enum(..., name='x').create(op.get_bind(), checkfirst=True)` antes,
  e `create_type=False` no Enum da coluna. No `downgrade`: `sa.Enum(name='x').drop(...)`
  além do `drop_column`. A revisão pode não pegar — o banco pega. E graças ao **DDL
  transacional** do Postgres, uma migration que falha **desfaz tudo** (sem meio-caminho).
- **Add coluna NOT NULL em tabela com dados** falha (não sabe o que pôr nas linhas
  antigas). Em produção: nullable → backfill → NOT NULL. Em dev: limpar os dados
  (filhos antes dos pais, por causa da FK) e migrar com a tabela vazia.
- **Ordem das rotas importa** — o FastAPI casa de cima pra baixo. Rota **específica**
  (`/usuarios/me`) tem que vir **antes** da rota com parâmetro (`/usuarios/{id}`),
  senão `"me"` é tratado como id e falha o parse (`int_parsing` → 422).
- **Default de parâmetro roda na definição** (não na chamada) — reprise do nugget do
  `-> Decimal`. `def exigir_admin(u = Depends(get_current_user))` exige
  `get_current_user` **definida acima**, senão `NameError` no import.
- **Segredo assina, não esconde** — o payload de um JWT é base64 **legível por
  qualquer um**. Nunca ponha dado sensível nele; o que impede forjar é a assinatura
  com `JWT_SECRET` (mudou 1 byte do token → 401).
- **Autogenerate tem pontos cegos** — não detecta constraint **UNIQUE** (escreve à
  mão) nem CHECK. E a migration reflete o model **no instante em que foi gerada**:
  mudar o model depois exige nova revisão; editar o arquivo já aplicado não re-roda
  (use `alembic stamp <rev>` p/ mover só o ponteiro e então `upgrade`). Sempre
  **testar de verdade** (inserir a duplicata), não confiar em "gerou = protegeu".
- **Reconstruir do zero é o teste real** (`downgrade base → upgrade head`): pegou 2
  bugs invisíveis no dia-a-dia — (1) `drop_constraint(None, ...)` de FK **sem nome**
  → dar o nome real (`<tabela>_<coluna>_fkey`); (2) `drop_table` de tabela com ENUM
  **deixa o tipo órfão** → o downgrade tem que `sa.Enum(name='x').drop(op.get_bind())`
  (contraparte da armadilha da lição 19).
