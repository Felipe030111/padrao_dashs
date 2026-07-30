# 3 · Filtros

Peças de filtro reutilizáveis + o separador de milhar BR.

## Separador de milhar (Jinja)
```python
from filtros import mil
app.jinja_env.filters["mil"] = mil
```
No template: `{{ valor|mil }}` → `1.234.567,89`

## Seletor por botões (ex.: escolher a obra)
```python
from filtros import option_buttons, FILTROS_CSS
html = option_buttons(
    items=[("114","#114 · Caracol"), ("111","#111 · Pacote 1B2"), ("GERAL","GERAL")],
    selected=obra_sel, base_url="/app/importacoes", param="obra", extra_params=f"ano={ano}")
```
O botão selecionado fica verde. Inclua `FILTROS_CSS` no `<style>`.

## Filtro de competência (mês + ano)
```python
from filtros import month_year_bar
html = month_year_bar("/app/importacoes", ano=2026, sel_mes=5, extra_params=f"obra={obra}")
```
Leia o mês em JS: `document.getElementById('selMes').value` (`"01".."12"`).

## Padrão de tela (do VAD)
Coloque **obra + competência no topo (passo 1)**; a grade/consolidado abaixo passam a
ser **daquela obra**. Assim o "verdinho" significa "essa obra, esse mês".
