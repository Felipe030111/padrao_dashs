# padrao_dashs — Padrões reutilizáveis de dashboards (modelo VAD)

Kit de peças prontas para montar um dashboard novo no mesmo padrão do **Dash VAD**
(Flask + páginas HTML geradas por Python + dados no CatWorld). Copie a pasta do
padrão que precisa e siga o `README.md` de cada uma.

## Princípio central
> **Acesso (login) → banco Postgres.  Dados importados → CatWorld.**

Veja [`docs/arquitetura-dados.md`](docs/arquitetura-dados.md) para o porquê e o passo a passo.

## Padrões disponíveis

| Pasta | O que é | Arquivo principal |
|---|---|---|
| [`1-acesso/`](1-acesso/) | Login/usuários/permissões (Flask + Postgres) | `auth.py` |
| [`2-menu/`](2-menu/) | Menu lateral (sidebar) configurável + CSS | `sidebar.py` |
| [`3-filtros/`](3-filtros/) | Filtros: botões de seleção, competência (mês/ano), separador de milhar | `filtros.py` |
| [`4-drill-excel/`](4-drill-excel/) | Drill (modal de detalhe) com **exportação em Excel** | `drill.py`, `export_excel.py` |
| [`5-dados-catworld/`](5-dados-catworld/) | Ler/gravar dados no CatWorld via API | `catworld_client.py` |

## Como começar um dash novo
1. **Acesso:** crie o banco `<projeto>_bi` no Postgres e use `1-acesso/auth.py`.
2. **Menu:** defina suas seções e use `2-menu/sidebar.py`.
3. **Dados:** crie/reuse um dataset no CatWorld e use `5-dados-catworld/catworld_client.py`.
4. **Filtros/Drill:** adicione conforme a tela (`3-filtros`, `4-drill-excel`).
5. Copie `.env.example` → `.env`, preencha, e **nunca versione o `.env`**.

> Cada pasta é independente e comentada. Não é um framework — são **peças** para copiar e adaptar.
