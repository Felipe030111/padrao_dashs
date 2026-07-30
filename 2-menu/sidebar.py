# -*- coding: utf-8 -*-
"""
Padrão de MENU — sidebar (menu lateral) configurável, igual à do Dash VAD.

Defina suas SEÇÕES e chame build_sidebar(...). Suporta:
- modo standalone (páginas .html soltas): mostra tudo, links diretos;
- modo servidor (com login): mostra só os módulos liberados ao usuário.

Ex.:
    SECTIONS = [
      ("Vendas", [
        ("faturamento", "bar-chart-3", "Faturamento", "painel-faturamento.html"),
        ("resultado",   "trending-up", "Resultado",   "resultado-obra.html"),
      ]),
      ("Config", [("admin", "settings", "Configurações", "admin")]),
    ]
    html = build_sidebar(SECTIONS, active="faturamento",
                         allowed={"faturamento"}, is_admin=False,
                         logo_html='<img src="...">',
                         admin_only={"admin"})
    # inclua SIDEBAR_CSS no seu <style> e o ícone via sua função (ou emoji).
"""
import os, re

def lucide(name, icons_dir="icons"):
    """Lê um SVG do Lucide (icons/<name>.svg). Se não achar, devolve ''."""
    fn = os.path.join(icons_dir, name + ".svg")
    if not os.path.exists(fn):
        return ""
    s = open(fn, encoding="utf-8").read()
    inner = re.sub(r"^.*?<svg[^>]*>", "", s, flags=re.S)
    inner = re.sub(r"</svg>.*$", "", inner, flags=re.S).strip()
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
            'stroke-linejoin="round">' + inner + '</svg>')

def build_sidebar(sections, active, allowed=None, is_admin=False,
                  logo_html="<b>LOGO</b>", admin_only=None, icon_fn=lucide,
                  foot=("Gestão inteligente.", "Resultados reais.")):
    """
    sections   : [(titulo_secao, [(chave, icone, rotulo, href), ...]), ...]
    active     : chave do item ativo
    allowed    : None = standalone (mostra tudo). set(...) = só os liberados.
    admin_only : set de chaves que só aparecem para admin (ex.: {"admin"}).
    icon_fn    : função (nome_icone)->svg/html. Troque por emoji se preferir.
    """
    admin_only = admin_only or set()
    def visible(key):
        if allowed is None: return True
        if key in admin_only: return bool(is_admin)
        return key in allowed
    parts = ['<div class="left-strip"></div>', '<aside class="side">',
             f'<div class="logo">{logo_html}</div>', '<div class="nav-wrap">']
    for sec, items in sections:
        vis = [it for it in items if visible(it[0])]
        if not vis: continue
        parts.append(f'<div class="nav-section"><div class="nav-sec-title">{sec}</div>')
        for key, icon, label, href in vis:
            tag = "a" if href else "div"
            attr = f' href="{href}"' if href else ""
            on = " on" if key == active else ""
            parts.append(f'<{tag} class="nav{on}"{attr}><span class="chip">{icon_fn(icon)}</span>'
                         f'<span class="lbl">{label}</span></{tag}>')
        parts.append('</div>')
    logout = '<a class="logout" href="/logout">Sair</a>' if allowed is not None else ''
    parts.append('</div><div class="foot">'
                 f'<b>{foot[0]}</b><span>{foot[1]}</span>' + logout + '</div></aside>')
    return "\n".join(parts)

# CSS da sidebar — inclua no <style> da página. Usa variáveis CSS (defina no :root):
#   --borda, --red, --green, --vermelho-claro, --icone-fundo
SIDEBAR_CSS = """
.left-strip{width:8px;background:#11181b;flex-shrink:0}
.side{width:230px;background:#fff;color:#656d79;display:flex;flex-direction:column;flex-shrink:0;border-right:1px solid var(--borda);padding:0 12px;overflow-y:auto}
.side .logo{min-height:64px;padding:10px 7px 8px;display:flex;align-items:center;justify-content:center;border-bottom:1px solid var(--borda)}
.side .logo img{width:150px;max-height:46px;object-fit:contain}
.nav-wrap{flex:1;padding:12px 5px 14px}
.nav-sec-title{margin:0 7px 6px;color:#9ca3af;font-size:8.5px;font-weight:800;letter-spacing:1px;text-transform:uppercase}
.nav-section{margin-bottom:14px}
.nav{position:relative;min-height:43px;margin-bottom:3px;padding:7px 9px;display:flex;align-items:center;gap:11px;border:1px solid transparent;border-radius:12px;color:#656d79;cursor:pointer;text-decoration:none}
.nav .chip{width:29px;height:29px;flex-shrink:0;display:flex;align-items:center;justify-content:center;border-radius:9px;background:var(--icone-fundo);color:#8c94a0}
.nav .chip svg{width:15px;height:15px}
.nav .lbl{flex:1;font-size:11.5px;font-weight:750}
.nav:hover{background:#f7f8fa}
.nav.on{color:var(--red);background:var(--vermelho-claro);border-color:#bfe0cf}
.nav.on .chip{color:#fff;background:linear-gradient(145deg,#0a7a48,#005330);box-shadow:0 5px 12px rgba(0,83,48,.25)}
.nav.on::after{content:"";position:absolute;top:50%;right:-6px;width:3px;height:22px;border-radius:10px;background:var(--red);transform:translateY(-50%)}
.side .foot{padding:12px 10px 14px;border-top:1px solid var(--borda)}
.side .foot b{color:#1f2933;font-size:11px;font-weight:800;display:block}
.side .foot span{color:var(--green);font-size:11px;font-weight:600}
.side .foot .logout{display:flex;align-items:center;justify-content:center;gap:6px;margin-top:11px;color:#8d95a3;text-decoration:none;font-size:11px;font-weight:700;border:1px solid var(--borda);border-radius:9px;padding:8px 10px}
.side .foot .logout:hover{background:var(--vermelho-claro);color:var(--red);border-color:#bfe0cf}
"""
