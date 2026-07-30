# -*- coding: utf-8 -*-
"""
Padrão de ACESSO — login/usuários/permissões com Flask + Postgres.

Regra do padrão: usuários ficam num banco Postgres dedicado (`<projeto>_bi`),
NUNCA no CatWorld (que é camada de dados/BI). Veja docs/arquitetura-dados.md.

Uso mínimo:
    import auth
    auth.configure(os.getenv("APP_DB_DSN"), modules=["faturamento","dre"])
    auth.init_users_db()                       # cria tabela users + admin/admin

    @app.route("/login", methods=["GET","POST"])
    def login():
        if request.method=="POST":
            u = auth.verify_login(request.form["username"], request.form["password"])
            if u: session["uid"]=u["id"]; return redirect("/")
            flash("Usuário ou senha inválidos.")
        return render_template_string(LOGIN_HTML)

    @app.route("/")
    @auth.login_required
    def home(): ...

    @app.route("/admin")
    @auth.admin_required
    def admin(): ...
"""
import json
from functools import wraps
import psycopg2
from psycopg2.extras import DictCursor
from flask import session, redirect, url_for, request, abort
from werkzeug.security import generate_password_hash, check_password_hash

_DSN = ""
_MODULES = []      # lista de chaves de módulo que existem no app (p/ permissões)

def configure(dsn, modules=None):
    global _DSN, _MODULES
    _DSN = dsn or ""
    _MODULES = list(modules or [])

# --------- camada de banco (adapta Postgres à API estilo sqlite) ----------
class _Pg:
    def __init__(self):
        self._c = psycopg2.connect(_DSN, cursor_factory=DictCursor)
    def execute(self, sql, params=()):
        cur = self._c.cursor(); cur.execute(sql.replace("?", "%s"), params); return cur
    def __enter__(self): return self
    def __exit__(self, et, ev, tb):
        try: self._c.commit() if et is None else self._c.rollback()
        finally: self._c.close()

def db():
    return _Pg()

def init_users_db():
    """Cria a tabela users e um admin/admin inicial (troque a senha depois!)."""
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL, name TEXT, pwhash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0, modules TEXT DEFAULT '[]', active INTEGER DEFAULT 1)""")
        n = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if n == 0:
            c.execute("INSERT INTO users(username,name,pwhash,is_admin,modules,active) VALUES(?,?,?,?,?,1)",
                      ("admin", "Administrador", generate_password_hash("admin"), 1,
                       json.dumps(_MODULES)))
            print(">> Usuario inicial criado: admin / admin  (TROQUE a senha!)")

# ------------------------------ consultas ------------------------------
def get_user(uid):
    with db() as c:
        r = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        return dict(r) if r else None

def current_user():
    uid = session.get("uid")
    return get_user(uid) if uid else None

def user_modules(u):
    if not u: return set()
    if u["is_admin"]: return set(_MODULES)
    try: return set(json.loads(u["modules"] or "[]"))
    except Exception: return set()

def verify_login(username, password):
    """Retorna o usuário (dict) se as credenciais baterem e estiver ativo; senão None."""
    with db() as c:
        r = c.execute("SELECT * FROM users WHERE username=? AND active=1", ((username or "").strip(),)).fetchone()
    if r and check_password_hash(r["pwhash"], password or ""):
        return dict(r)
    return None

def save_user(username, name, password, is_admin=0, modules=None):
    """Cria/atualiza usuário. Retorna (ok, msg)."""
    modules = json.dumps(list(modules or []))
    try:
        with db() as c:
            c.execute("""INSERT INTO users(username,name,pwhash,is_admin,modules,active)
                         VALUES(?,?,?,?,?,1)
                         ON CONFLICT(username) DO UPDATE SET
                           name=EXCLUDED.name, is_admin=EXCLUDED.is_admin, modules=EXCLUDED.modules""",
                      ((username or "").strip(), name, generate_password_hash(password), int(is_admin), modules))
        return True, "Usuário salvo."
    except psycopg2.IntegrityError:
        return False, "Usuário já existe."

# ------------------------------ guards ------------------------------
def login_required(f):
    @wraps(f)
    def w(*a, **k):
        if not current_user():
            return redirect(url_for("login", next=request.path))
        return f(*a, **k)
    return w

def admin_required(f):
    @wraps(f)
    def w(*a, **k):
        u = current_user()
        if not u: return redirect(url_for("login"))
        if not u["is_admin"]: abort(403)
        return f(*a, **k)
    return w
