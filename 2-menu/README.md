# 2 · Menu (sidebar)

Menu lateral configurável, idêntico ao do Dash VAD. Funciona em 2 modos:
- **standalone** (`allowed=None`): mostra tudo, links diretos (bom p/ HTML solto);
- **servidor** (`allowed=set(...)`): mostra só os módulos liberados ao usuário.

## Uso
```python
from sidebar import build_sidebar, SIDEBAR_CSS, lucide

SECTIONS = [
  ("Vendas", [
    ("faturamento", "bar-chart-3", "Faturamento", "painel-faturamento.html"),
    ("resultado",   "trending-up", "Resultado",   "resultado-obra.html"),
  ]),
  ("Config", [("admin", "settings", "Configurações", "admin")]),
]

html = build_sidebar(SECTIONS, active="faturamento",
                     allowed=auth.user_modules(user), is_admin=user["is_admin"],
                     logo_html='<img src="data:image/png;base64,...">',
                     admin_only={"admin"})
```
Inclua `SIDEBAR_CSS` no `<style>`. As cores usam variáveis CSS — defina no `:root`:
`--borda, --red, --green, --vermelho-claro, --icone-fundo`.

## Ícones
Por padrão usa SVGs do [Lucide](https://lucide.dev) numa pasta `icons/<nome>.svg`
(`icon_fn=lucide`). Sem os SVGs, passe `icon_fn=lambda n: "•"` ou use emoji.
