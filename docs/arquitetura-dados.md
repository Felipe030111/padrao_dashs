# Padrão de dados: Usuários no Postgres, Dados no CatWorld

Guia reutilizável para qualquer projeto de BI/app similar (Flask ou outro).
Explica **onde cada coisa mora** e **como o app grava/lê dados no CatWorld**.

---

## 1. O princípio (a regra que vale pra todo projeto)

Separe **acesso** de **dado**:

| Tipo | Onde fica | Por quê |
|---|---|---|
| **Usuários / login / permissões** | Banco **Postgres** dedicado (ex.: `xxx_bi`), tabela `users` | É infra do app. Precisa ser persistente e privado. |
| **Qualquer dado que o app gera/importa** (provisões, planilhas, cadastros, uploads…) | **CatWorld**, num **dataset** | É dado de negócio. No CatWorld ele junta com o resto do BI e vai pro **Power BI** automaticamente. |

> Regra prática: **login → Postgres. Qualquer upload/dado → CatWorld.**
> O caminho exato no CatWorld (qual projeto/dataset/tabela) você define por projeto.

**Por que não jogar tudo no Postgres?** Porque o dado de negócio precisa aparecer no
BI/Power BI junto com o resto. E por que não jogar usuário no CatWorld? Porque o CatWorld
é camada de dados/BI (não é um authserver), e login tem que ser rápido e privado.

### 1.1. Banco (Postgres) ≠ Dataset (CatWorld) — o que criar em cada lado

Não é "criar dataset nos dois lados". São coisas diferentes:

| Lado | O que você cria | Guarda o quê |
|---|---|---|
| **Postgres** | um **banco de dados** (`<projeto>_bi`) com a tabela `users` | usuários/acesso |
| **CatWorld** | um **dataset** (novo **ou** reusa um existente); cada upload vira uma **tabela** dentro dele | dados importados |

- No **Postgres** não existe "dataset" — lá é **banco** (`CREATE DATABASE <projeto>_bi;`). Um por projeto/cliente, só pra login.
- No **CatWorld** você **não precisa** de um dataset novo por tabela. Um dataset tem **várias tabelas**. No VAD, por exemplo, **não criamos dataset** — usamos o `GERAL` (que já existia) e o upload criou a tabela `provisoes` dentro dele.
  - Crie um dataset novo só se quiser **separar por tema/projeto** (ex.: "RH", "Financeiro"). É escolha organizacional.

**Por projeto novo, no mínimo:** 1 **banco** no Postgres (`<projeto>_bi`) + 1 **dataset** no CatWorld (novo ou reusado) do qual você anota o **Dataset ID**.

---

## 2. Como o CatWorld recebe dado (importante!)

O CatWorld **NÃO tem "INSERT ao vivo"**:
- A API **OData** e a **API REST de SQL** são **somente leitura** (um `POST` de escrita no OData devolve **405**).
- Só há **duas formas de gravar**:
  1. **Upload de arquivo** (CSV/XLSX) → vira uma tabela no dataset. **← é o que usamos.**
  2. **Fonte conectada** → o CatWorld lê ao vivo de um banco externo (Postgres/SQL Server).

Usamos **upload via API** (mode `replace` = substitui a tabela inteira a cada gravação;
existe também `upsert` por chave). Assim o dado fica **fisicamente dentro do CatWorld**.

---

## 3. O fluxo de UPLOAD via API (o "pulo do gato")

Base da API: `https://catworld.77indicadores.com.br/api/v1`
Autenticação: header `Authorization: Bearer <TOKEN>` (token de escopo **GLOBAL:WRITE**).

O upload é **multi-etapa**:

1. **Cria o upload** (manda os metadados):
   ```
   POST /api/v1/uploads
   { "filename": "dados.csv", "sizeBytes": <n>, "fileHash": "<md5>",
     "datasetId": "<DATASET_ID>", "mode": "replace" }
   → devolve { upload: { id }, sas: { url }, skip? }
   ```
   (Se `skip=true`, o hash é igual ao último — nada a fazer.)

2. **Envia os bytes** do arquivo **GZIPADOS** para a URL retornada:
   ```
   PUT {sas.url}
   headers: content-type: application/octet-stream, content-encoding: gzip
   body: <arquivo comprimido com gzip>
   ```

3. **Confirma** (dispara o processamento) — a ação vai na **query string**:
   ```
   POST /api/v1/uploads/{id}?action=uploaded
   ```

4. **Processa em background** → faça *poll* até concluir:
   ```
   GET /api/v1/uploads/{id}   → status: PENDING_UPLOAD → ... → COMPLETED (ou FAILED)
   ```

Para **ler de volta** (SQL somente-leitura):
```
POST /api/v1/queries
{ "sql": "SELECT * FROM <tabela>", "datasetId": "<DATASET_ID>" }
→ { data: { columns, rows } }
```

> Existe um pacote Python privado `catworld` (`CatworldClient.upload/query`), mas ele
> **não está no PyPI**. Por isso implementamos o fluxo na mão (só stdlib) — assim o
> deploy não depende de um pacote privado. Veja o módulo em `catworld_prov.py`.

---

## 4. Módulo reutilizável (genérico)

Copie `catworld_prov.py` para o novo projeto. Ele é genérico: `read()` faz `SELECT` e
`replace(rows)` sobe a tabela inteira. Para adaptar, mude só o **nome da tabela** e as
**colunas** dentro do módulo (ou generalize recebendo o nome da tabela por parâmetro).

Uso no código:
```python
from catworld_prov import CatworldProv
cw = CatworldProv(ROOT, TOKEN, DATASET_ID)
linhas = cw.read()                 # lê tudo
cw.replace(linhas)                 # sobe tudo (mode=replace)
cw.upsert(...); cw.delete(...)     # helpers de 1 registro (lê + mescla + sobe)
```

---

## 5. Variáveis de ambiente (o que setar em cada projeto)

Ficam no `.env` **local**, e **no painel do host** em produção (o `.env` é gitignored e
**não vai** para a imagem Docker):

```
# CatWorld
CATWORLD_API_ROOT=https://catworld.77indicadores.com.br
CATWORLD_API_TOKEN=cw_live_...               # token GLOBAL:WRITE (NÃO commitar)
CATWORLD_<X>_DATASET_ID=<uuid do dataset>    # o dataset onde os dados vão

# Postgres (só usuários/acesso)
VAD_DB_DSN=host=... port=... user=... password=... dbname=<projeto>_bi

# Flask
SECRET_KEY=<aleatória>
```

⚠️ **Produção:** `VAD_DB_DSN` é obrigatória no **boot** (sem ela o gunicorn não sobe →
proxy responde *"no available server"*). Se o `Dockerfile` roda um build de dashboards
(`build_all.py`), o **token** e a **base OData** também precisam existir na etapa de **build**.

---

## 6. Checklist para um projeto NOVO

1. **Criar o banco de usuários** no Postgres: `CREATE DATABASE <projeto>_bi;` (só `users`).
2. **No CatWorld** (`/settings/…`): criar/escolher o **projeto** e o **dataset** que vai
   receber os dados; anotar o **Dataset ID**.
3. **Token**: em `/tokens`, gerar (ou reusar) um token com escopo **GLOBAL:WRITE**.
4. **Copiar `catworld_prov.py`** para o projeto e ajustar tabela/colunas.
5. **Ligar o app**: onde antes salvava dado local/Postgres, chamar `cw.replace(...)`;
   onde lia, chamar `cw.read()`.
6. **Preencher `.env`** (local) e **cadastrar as variáveis no host** (produção).
7. Conferir round-trip: salvar um registro pelo app → aparecer no dataset (OData/Power BI).

---

## 7. Onde configurar no CatWorld (telas)

- **Conexões de banco externo** (se for usar "fonte ao vivo"): `…/settings/connections`
- **Tokens de API**: menu **Tokens** (`/tokens`) — cada token tem escopo READ ou WRITE.
- **Datasets / upload manual**: dentro do **projeto** → dataset → seção **Novo upload**.
- **Conectar ao Power BI**: botão no dataset (usa a API OData de leitura).
