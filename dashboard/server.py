#!/usr/bin/env python3
"""Local dashboard: search all four services in dataExports/ at once.

Run:  python3 dashboard/server.py        (then open http://localhost:8000)
Only the Python standard library is used. Nothing is sent over the network.
"""
import csv, json, os, re, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS = os.path.join(ROOT, "dataExports")
HERE = os.path.dirname(os.path.abspath(__file__))
SERVICES = ["gmail", "github", "notion", "supabase"]


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def load_gmail():
    items = []
    d = os.path.join(EXPORTS, "gmail")
    for name in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if not name.endswith(".json"):
            continue
        p = os.path.join(d, name)
        m = json.load(open(p, encoding="utf-8"))
        items.append({
            "service": "gmail",
            "title": m.get("subject", "(no subject)"),
            "text": " ".join([m.get("subject", ""), m.get("from", ""), " ".join(m.get("to", [])),
                              " ".join(m.get("labels", [])), m.get("body", "")]),
            "meta": f"From {m.get('from', '?')} on {m.get('date', '?')}",
            "file": rel(p),
            "url": m.get("viewUrl", ""),
        })
    return items


def load_github():
    items = []
    d = os.path.join(EXPORTS, "github")
    for name in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if not name.endswith(".json"):
            continue
        p = os.path.join(d, name)
        i = json.load(open(p, encoding="utf-8"))
        items.append({
            "service": "github",
            "title": f"#{i.get('number')} {i.get('title', '')}",
            "text": " ".join([i.get("title", ""), i.get("body") or "", " ".join(i.get("labels", [])), i.get("state", "")]),
            "meta": f"{i.get('state', '?')} issue, labels: {', '.join(i.get('labels', [])) or 'none'}, created {i.get('created_at', '?')}",
            "file": rel(p),
            "url": i.get("url", ""),
        })
    return items


def parse_front_matter(text):
    """Very small YAML reader for the flat front matter we write."""
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {}, text
    meta, props, in_props = {}, {}, False
    for line in m.group(1).splitlines():
        if line.startswith("properties:"):
            in_props = True
            continue
        mm = re.match(r"^(\s*)([^:]+):\s*(.*)$", line)
        if not mm:
            continue
        val = mm.group(3).strip().strip('"')
        if in_props and mm.group(1):
            props[mm.group(2).strip()] = val
        else:
            in_props = False
            meta[mm.group(2).strip()] = val
    meta["properties"] = props
    return meta, m.group(2)


def load_notion():
    items = []
    d = os.path.join(EXPORTS, "notion")
    for name in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if not name.endswith(".md"):
            continue
        p = os.path.join(d, name)
        meta, body = parse_front_matter(open(p, encoding="utf-8").read())
        props = meta.get("properties", {})
        items.append({
            "service": "notion",
            "title": meta.get("title", name),
            "text": " ".join([meta.get("title", ""), " ".join(props.values()), body]),
            "meta": f"Stage: {props.get('Stage', '?')}, brand: {props.get('Brand', '?')}, source: {props.get('Lead Source', '?')}",
            "file": rel(p),
            "url": meta.get("url", ""),
        })
    return items


def load_supabase():
    items = []
    d = os.path.join(EXPORTS, "supabase")
    for name in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if not name.endswith(".json") or name == "schema.json":
            continue
        p = os.path.join(d, name)
        t = json.load(open(p, encoding="utf-8"))
        table = t.get("table", name)
        for r in t.get("rows", []):
            items.append({
                "service": "supabase",
                "title": f"{table} #{r.get('id')}: {r.get('client_name', '')} · {r.get('motorcycle', '')}",
                "text": " ".join(f"{k} {v}" for k, v in r.items()),
                "meta": f"Client: {r.get('client_name', '?')}, motorcycle: {r.get('motorcycle', '?')}",
                "file": rel(p),
                "url": "",
            })
    return items


def load_all():
    return load_gmail() + load_github() + load_notion() + load_supabase()


def snippet(text, terms, width=160):
    text = re.sub(r"\s+", " ", text).strip()
    low = text.lower()
    pos = min([low.find(t) for t in terms if low.find(t) >= 0] or [0])
    start = max(0, pos - width // 3)
    s = text[start:start + width]
    return ("…" if start > 0 else "") + s + ("…" if start + width < len(text) else "")


def search(query, services):
    terms = [t for t in re.split(r"\s+", query.lower().strip()) if t]
    results = []
    for it in load_all():
        if it["service"] not in services:
            continue
        hay = it["text"].lower()
        if terms and not all(t in hay for t in terms):
            continue
        score = sum(3 for t in terms if t in it["title"].lower()) + sum(hay.count(t) for t in terms)
        results.append((score, it))
    results.sort(key=lambda x: -x[0])
    out = []
    for score, it in results:
        out.append({k: it[k] for k in ("service", "title", "meta", "file", "url")} | {"snippet": snippet(it["text"], terms)})
    return out


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, ctype, body):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/api/search":
            qs = parse_qs(u.query)
            q = qs.get("q", [""])[0]
            svc = [s for s in qs.get("services", [",".join(SERVICES)])[0].split(",") if s in SERVICES]
            res = search(q, svc)
            counts = {s: sum(1 for r in res if r["service"] == s) for s in SERVICES}
            self._send(200, "application/json", json.dumps({"query": q, "total": len(res), "counts": counts, "results": res}))
        elif u.path in ("/", "/index.html"):
            self._send(200, "text/html; charset=utf-8", open(os.path.join(HERE, "index.html"), encoding="utf-8").read())
        elif u.path == "/api/file":
            f = parse_qs(u.query).get("path", [""])[0]
            full = os.path.realpath(os.path.join(ROOT, f))
            if not full.startswith(os.path.realpath(EXPORTS) + os.sep) or not os.path.isfile(full):
                self._send(404, "text/plain", "Not found")
            else:
                self._send(200, "text/plain; charset=utf-8", open(full, encoding="utf-8").read())
        else:
            self._send(404, "text/plain", "Not found")

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--search":  # quick CLI test: server.py --search "financing"
        res = search(sys.argv[2], SERVICES)
        for s in SERVICES:
            print(s, sum(1 for r in res if r["service"] == s))
        sys.exit(0)
    port = int(os.environ.get("PORT", "8000"))
    print(f"Dashboard running at http://localhost:{port}  (Ctrl+C to stop)")
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
