# -*- coding: utf-8 -*-
"""
Padrão de FILTROS — peças de UI reutilizáveis para as telas.

Inclui:
  - mil()            : filtro de número BR (1.234.567,89) p/ Jinja
  - option_buttons() : seletor por botões (ex.: escolher a obra/empreendimento)
  - month_year_bar() : filtro de competência (mês + ano) com setas
  - FILTROS_CSS      : CSS das peças acima

Registrar o filtro no Flask:
    from filtros import mil
    app.jinja_env.filters["mil"] = mil
No template:  {{ valor|mil }}   ->  1.234.567,89
"""

def mil(v):
    """Número no padrão BR com separador de milhar: 1.234.567,89"""
    try:
        v = float(v)
    except (TypeError, ValueError):
        return v
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def option_buttons(items, selected, base_url, param="obra", extra_params=""):
    """
    Seletor por botões (o selecionado fica destacado).
    items        : [(valor, rotulo), ...]
    selected     : valor atualmente selecionado
    base_url     : ex. "/app/importacoes"
    param        : nome do parâmetro na URL
    extra_params : querystring extra a preservar, ex. "ano=2026"
    """
    sep = ("&" + extra_params) if extra_params else ""
    out = ['<div class="obsel">']
    for val, lbl in items:
        on = " on" if str(val) == str(selected) else ""
        out.append(f'<a class="obtn{on}" href="{base_url}?{param}={val}{sep}">{lbl}</a>')
    out.append("</div>")
    return "\n".join(out)


def month_year_bar(base_url, ano, sel_id="selMes", meses=None, extra_params="",
                   sel_mes=None):
    """
    Filtro de competência: <select> de mês + navegação de ano (‹ ano ›).
    Retorna o HTML; leia o mês em JS via document.getElementById(sel_id).value ("01".."12").
    """
    meses = meses or ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
    sep = ("&" + extra_params) if extra_params else ""
    opts = []
    for i, mn in enumerate(meses, 1):
        s = " selected" if sel_mes == i else ""
        opts.append(f'<option value="{i:02d}"{s}>{mn}</option>')
    return (
        '<div class="fcomp"><span class="flbl">Competência</span>'
        f'<select id="{sel_id}">{"".join(opts)}</select>'
        f'<a class="yb" href="{base_url}?ano={ano-1}{sep}" title="Ano anterior">‹</a>'
        f'<span class="yy">{ano}</span>'
        f'<a class="yb" href="{base_url}?ano={ano+1}{sep}" title="Próximo ano">›</a>'
        '</div>'
    )


FILTROS_CSS = """
.obsel{display:flex;flex-wrap:wrap;gap:8px}
.obtn{display:inline-block;padding:8px 13px;border:1px solid #e4e7eb;border-radius:9px;background:#f9fafb;color:#405048;text-decoration:none;font-size:12px;font-weight:800}
.obtn:hover{border-color:#bfe0cf;background:#f4faf6}
.obtn.on{background:linear-gradient(145deg,#0a7a48,#005330);color:#fff;border-color:#005330}
.fcomp{display:flex;align-items:center;gap:8px}
.flbl{font-size:10px;font-weight:800;color:#7a828e;text-transform:uppercase}
.fcomp select{min-width:130px;border:1px solid #e4e7eb;border-radius:9px;padding:9px 10px;font-size:13px;font-family:inherit}
.fcomp .yb{width:30px;height:36px;display:flex;align-items:center;justify-content:center;border:1px solid #e4e7eb;border-radius:8px;color:#405048;text-decoration:none;font-weight:800}
.fcomp .yb:hover{background:#f4faf6;border-color:#bfe0cf}
.fcomp .yy{font-size:15px;font-weight:800;color:#0b3d24;min-width:48px;text-align:center}
"""
