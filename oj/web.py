"""Web 做题界面:标准库 http.server 提供 JSON API + 托管单页。

API:
  GET  /api/companies                      -> ["tencent", ...]
  GET  /api/problems?company=tencent       -> [{frontend_id,title,title_slug,difficulty,solved}]
  GET  /api/problem?company=..&slug=..      -> {title,difficulty,url,content_md,code,meta,has_expected}
  POST /api/run  {company,slug,code}        -> {ac,passed,total,cases:[...]}  (不落盘,临时判题)
  POST /api/save {company,slug,code}        -> {ok, path}                      (保存到 solutions/)
"""
import json
import tempfile
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from oj import config, store, runner

_WEB_DIR = Path(__file__).resolve().parent / "web_static"


def run_code(company: str, slug: str, code: str) -> dict:
    """用用户提交的代码临时判题,不写进 solutions/。"""
    problem = store.load_problem(company, slug)
    tmp = Path(tempfile.gettempdir()) / f"oj_web_{company}_{slug.replace('/', '_')}.py"
    tmp.write_text(code)
    try:
        return runner.run_solution(str(tmp), problem)
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass


def _problem_payload(company: str, slug: str) -> dict:
    p = store.load_problem(company, slug)
    sp = store.solution_path(company, p["frontend_id"], p["title_slug"])
    # 已有题解则回填用户代码,否则用模板
    if sp.exists():
        code = sp.read_text()
    else:
        from oj import render
        code = render.build_solution_template(p)
    d = store.problem_dir(company, p["frontend_id"], p["title_slug"])
    content_md = (d / "README.md").read_text() if (d / "README.md").exists() else ""
    return {
        "frontend_id": p["frontend_id"], "title": p["title"],
        "title_slug": p["title_slug"], "difficulty": p["difficulty"],
        "url": p.get("url", ""), "content_md": content_md, "code": code,
        "has_expected": bool(p["testcases"].get("expected")),
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass  # 静默

    def _send(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path, ctype: str):
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        try:
            if u.path in ("/", "/index.html"):
                return self._send_file(_WEB_DIR / "index.html", "text/html; charset=utf-8")
            if u.path == "/api/companies":
                return self._send(list(config.PLANS.keys()))
            if u.path == "/api/problems":
                company = q.get("company", [""])[0]
                return self._send(store.list_problems(company))
            if u.path == "/api/problem":
                company = q.get("company", [""])[0]
                slug = q.get("slug", [""])[0]
                return self._send(_problem_payload(company, slug))
            return self._send({"error": "not found"}, 404)
        except Exception as e:
            return self._send({"error": str(e)}, 500)

    def do_POST(self):
        u = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length) or b"{}")
        try:
            if u.path == "/api/run":
                result = run_code(data["company"], data["slug"], data["code"])
                return self._send(result)
            if u.path == "/api/save":
                p = store.load_problem(data["company"], data["slug"])
                sp = store.solution_path(data["company"], p["frontend_id"], p["title_slug"])
                sp.parent.mkdir(parents=True, exist_ok=True)
                sp.write_text(data["code"])
                return self._send({"ok": True, "path": str(sp)})
            return self._send({"error": "not found"}, 404)
        except Exception as e:
            return self._send({"error": str(e)}, 500)


def serve(host="127.0.0.1", port=8600):
    httpd = ThreadingHTTPServer((host, port), Handler)
    url = f"http://{host}:{port}/"
    print(f"做题界面已启动:{url}")
    print("按 Ctrl+C 停止。")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")
        httpd.shutdown()
