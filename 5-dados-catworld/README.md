# 5 · Dados no CatWorld

Ler e gravar dados de negócio no **CatWorld** (dataset), via API. O CatWorld
não tem INSERT ao vivo — grava por **upload** (mode=replace) e lê por **SQL**.
Detalhes e o "pulo do gato" do upload: veja [`../docs/arquitetura-dados.md`](../docs/arquitetura-dados.md).

`catworld_client.py` usa **só a stdlib** (urllib/gzip/hashlib) — não depende de pacote privado.

## Uso
```python
from catworld_client import CatworldProv   # (classe genérica; renomeie à vontade)
cw = CatworldProv(
    root=os.getenv("CATWORLD_API_ROOT"),
    token=os.getenv("CATWORLD_API_TOKEN"),      # escopo GLOBAL:WRITE
    dataset_id=os.getenv("CATWORLD_DATASET_ID"),
)

linhas = cw.read()                 # SELECT * (lista de dicts)
cw.replace(linhas)                 # sobe a tabela inteira (mode=replace)
cw.upsert(...); cw.delete(...)     # helpers de 1 registro (lê + mescla + sobe)
```

> `catworld_client.py` está montado para a tabela `provisoes` (colunas do VAD).
> Para outro projeto, ajuste o nome da tabela e as colunas (`COLS` e os `SELECT`),
> ou generalize recebendo o nome da tabela por parâmetro.

## Precisa por projeto
- Um **dataset** no CatWorld (novo ou reusado) → anote o **Dataset ID**.
- Um **token GLOBAL:WRITE** (tela `/tokens`).
- Variáveis no `.env`: `CATWORLD_API_ROOT`, `CATWORLD_API_TOKEN`, `CATWORLD_DATASET_ID`.
