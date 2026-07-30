# 4 · Drill (detalhe) com exportação em Excel

Clique numa linha/número → abre um modal com o detalhe → botão **Exportar Excel**.

## Peças
- `drill.py` — modal (HTML/CSS/JS) orientado a dados.
- `export_excel.py` — gera o `.xlsx` (openpyxl) e a Response de download.

## Montagem na página (dados embutidos)
```python
import json
from drill import DRILL_CSS, drill_modal_html, drill_js

# 1) na tabela principal, marque a linha com data-drill
#    <tr data-drill="114"><td>Obra #114</td>...</tr>

# 2) dados do detalhe por chave
dados = {
  "114": {"title":"Obra #114 — detalhe",
          "headers":["Conta","Realizado","Comparativo"],
          "rows":[["Mão de obra", "1.000,00", "1.200,00"], ...]},
}

pagina = f'''
<style>{DRILL_CSS}</style>
... tabela ...
{drill_modal_html(export_base="/export")}
<script>var DRILL_DATA = {json.dumps(dados)};</script>
<script>{drill_js(export_base="/export")}</script>
'''
```

## Rota de exportação (Flask)
```python
from export_excel import xlsx_response

@app.route("/export/<obra>.xlsx")
@auth.login_required
def export(obra):
    d = detalhe_da_obra(obra)               # mesma fonte do drill
    return xlsx_response(d["headers"], d["rows"],
                         filename=f"detalhe_{obra}.xlsx", sheet="Detalhe")
```

O botão "Exportar Excel" do modal aponta sozinho para `/export/<chave>.xlsx`.

## Variações
- **Drill no número específico**: coloque `data-drill` na `<td>` do número (não na linha)
  e use chaves compostas (ex.: `114|recebido`).
- **Sem servidor** (HTML solto): troque o export por geração client-side de CSV.
