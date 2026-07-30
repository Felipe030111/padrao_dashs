# -*- coding: utf-8 -*-
"""
Provisões no CatWorld (dataset GERAL) — sem Postgres.

O CatWorld não tem INSERT ao vivo: a gravação é por UPLOAD de arquivo (fluxo
multi-etapa) e a leitura é por SQL (POST /api/v1/queries). Este módulo replica
o fluxo oficial usando só a stdlib (urllib+gzip+hashlib), pra não depender do
pacote privado `catworld` e ficar deployável.

Fluxo de upload (descoberto no cliente oficial):
  1) POST /api/v1/uploads            {filename, sizeBytes, fileHash(md5), datasetId, mode}
  2) PUT  {sas.url}                  bytes GZIPADOS (content-encoding: gzip)
  3) POST /api/v1/uploads/{id}?action=uploaded
  4) processamento em background -> poll GET /api/v1/uploads/{id} até COMPLETED
"""
import io, csv, gzip, json, time, hashlib, urllib.request, urllib.error

COLS = ["obra", "competencia", "tipo", "valor_mes", "valor_acum", "colaboradores", "atualizado"]


class CatworldProv:
    def __init__(self, root, token, dataset_id, timeout=60):
        self.root = (root or "").rstrip("/")
        self.token = token or ""
        self.ds = dataset_id or ""
        self.timeout = timeout

    # ---------------- infra ----------------
    def _req(self, method, path, body=None, raw=None, extra_headers=None):
        url = path if path.startswith("http") else self.root + path
        headers = {"Authorization": "Bearer " + self.token}
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        elif raw is not None:
            data = raw
        if extra_headers:
            headers.update(extra_headers)
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            txt = r.read().decode("utf-8") or "{}"
        return json.loads(txt)

    def ok(self):
        return bool(self.root and self.token and self.ds)

    # ---------------- leitura ----------------
    def read(self):
        """Lê todas as provisões do CatWorld, já normalizadas nos tipos do app."""
        r = self._req("POST", "/api/v1/queries", body={
            "sql": "SELECT obra,competencia,tipo,valor_mes,valor_acum,colaboradores,atualizado FROM provisoes",
            "datasetId": self.ds,
        })
        rows = (r.get("data") or {}).get("rows", []) or []
        out = []
        for x in rows:
            out.append({
                "obra": str(x.get("obra") or "").strip(),
                "competencia": str(x.get("competencia") or "").strip(),
                "tipo": str(x.get("tipo") or "").strip().lower(),
                "valor_mes": _f(x.get("valor_mes")),
                "valor_acum": _f(x.get("valor_acum")),
                "colaboradores": _i(x.get("colaboradores")),
                "atualizado": str(x.get("atualizado") or ""),
            })
        return out

    # ---------------- escrita (substitui a tabela inteira) ----------------
    def replace(self, rows, wait=True):
        """Sobe o conjunto COMPLETO de provisões (mode=replace)."""
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(COLS)
        for x in rows:
            w.writerow([x.get("obra", ""), x.get("competencia", ""), x.get("tipo", ""),
                        x.get("valor_mes", 0), x.get("valor_acum", 0),
                        x.get("colaboradores", 0), x.get("atualizado", "")])
        content = buf.getvalue().encode("utf-8")
        fhash = hashlib.md5(content).hexdigest()

        created = self._req("POST", "/api/v1/uploads", body={
            "filename": "provisoes.csv", "sizeBytes": len(content),
            "fileHash": fhash, "datasetId": self.ds, "mode": "replace",
        })
        d = created.get("data") or created
        if d.get("skip"):
            return "SKIPPED"
        upid = d["upload"]["id"]
        sas = d["sas"]["url"]

        gz = gzip.compress(content)
        self._req("PUT", sas, raw=gz, extra_headers={
            "Content-Type": "application/octet-stream", "Content-Encoding": "gzip"})
        self._req("POST", "/api/v1/uploads/%s?action=uploaded" % upid)

        if not wait:
            return "PENDING"
        for _ in range(25):
            st = self._req("GET", "/api/v1/uploads/%s" % upid)
            status = (st.get("data") or {}).get("status")
            if status in ("COMPLETED", "FAILED"):
                return status
            time.sleep(1)
        return "PENDING"

    # ---------------- helpers de alto nível ----------------
    def upsert(self, obra, competencia, tipo, valor_mes, valor_acum, colaboradores, atualizado):
        rows = self.read()
        key = (obra, competencia, (tipo or "").lower())
        rows = [r for r in rows if (r["obra"], r["competencia"], r["tipo"]) != key]
        rows.append({"obra": obra, "competencia": competencia, "tipo": (tipo or "").lower(),
                     "valor_mes": valor_mes, "valor_acum": valor_acum,
                     "colaboradores": colaboradores, "atualizado": atualizado})
        return self.replace(rows)

    def delete(self, obra, competencia, tipo):
        rows = self.read()
        key = (obra, competencia, (tipo or "").lower())
        rows = [r for r in rows if (r["obra"], r["competencia"], r["tipo"]) != key]
        return self.replace(rows)


def _f(x):
    try: return float(str(x).replace(",", "."))
    except Exception: return 0.0

def _i(x):
    try: return int(float(x))
    except Exception: return 0
