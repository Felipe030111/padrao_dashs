# 1 · Acesso (login / usuários / permissões)

Login com **Flask + Postgres**. Usuários ficam num banco dedicado (`<projeto>_bi`),
nunca no CatWorld.

## Setup
1. Crie o banco no Postgres: `CREATE DATABASE projeto_bi;`
2. Ponha o DSN em `.env`: `APP_DB_DSN=host=... user=... password=... dbname=projeto_bi`
3. No app:
```python
import os, auth
auth.configure(os.getenv("APP_DB_DSN"), modules=["faturamento","dre","resultado"])
auth.init_users_db()          # cria tabela users + admin/admin (troque a senha!)
```

## Uso
```python
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = auth.verify_login(request.form["username"], request.form["password"])
        if u:
            session["uid"] = u["id"]; return redirect("/")
        flash("Usuário ou senha inválidos.")
    return render_template_string(LOGIN_HTML)

@app.route("/")            # exige login
@auth.login_required
def home(): ...

@app.route("/admin")       # exige admin
@auth.admin_required
def admin(): ...
```

## Permissões por módulo
- `auth.user_modules(u)` → conjunto de módulos que o usuário pode ver (admin vê tudo).
- Use isso para montar a sidebar (`allowed=`) e barrar rotas.

## Produção
`APP_DB_DSN` precisa existir no **boot** (senão o app não sobe). Cadastre no host,
não no git. Chame `init_users_db()` no import do módulo (WSGI/gunicorn não roda `__main__`).
