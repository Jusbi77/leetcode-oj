"""题库/题解的读写、路径解析、完成状态。纯文件系统操作,无网络。"""
import json
from pathlib import Path

from oj import config, render


def _root(root):
    return Path(root) if root else config.REPO_ROOT


def _problems(root):
    return _root(root) / "problems"


def _solutions(root):
    return _root(root) / "solutions"


def _dirname(frontend_id, title_slug):
    return f"{config.pad_id(frontend_id)}.{title_slug}"


def problem_dir(company, frontend_id, title_slug, root=None):
    return _problems(root) / company / _dirname(frontend_id, title_slug)


def solution_path(company, frontend_id, title_slug, root=None):
    return _solutions(root) / company / f"{_dirname(frontend_id, title_slug)}.py"


def save_problem(company, problem, root=None):
    """落盘 problem.json + testcases.json + README.md,返回题目目录。"""
    d = problem_dir(company, problem["frontend_id"], problem["title_slug"], root)
    d.mkdir(parents=True, exist_ok=True)
    meta_doc = {k: problem[k] for k in
                ("frontend_id", "title", "title_slug", "difficulty", "url", "meta", "code_snippet")
                if k in problem}
    (d / "problem.json").write_text(json.dumps(meta_doc, ensure_ascii=False, indent=2))
    (d / "testcases.json").write_text(json.dumps(problem["testcases"], ensure_ascii=False, indent=2))
    title = f'# {problem["frontend_id"]}. {problem["title"]}  [{problem["difficulty"]}]\n\n'
    link = f'> {problem.get("url", "")}\n\n'
    (d / "README.md").write_text(title + link + problem.get("content_md", "") + "\n")
    return d


def _find_dir(company, key, root=None):
    base = _problems(root) / company
    if not base.exists():
        raise FileNotFoundError(f"no problems for {company}")
    key = str(key)
    for d in sorted(base.iterdir()):
        if not d.is_dir():
            continue
        num, _, slug = d.name.partition(".")
        if slug == key or num == config.pad_id(key) or num == key:
            return d
    raise FileNotFoundError(f"problem not found: {company}/{key}")


def load_problem(company, key, root=None):
    """按 titleSlug 或题号读回合并后的 problem dict(含 testcases)。"""
    d = _find_dir(company, key, root)
    problem = json.loads((d / "problem.json").read_text())
    problem["testcases"] = json.loads((d / "testcases.json").read_text())
    return problem


def list_problems(company, root=None):
    """列出某公司全部题目及完成状态,按题号排序。"""
    base = _problems(root) / company
    out = []
    if not base.exists():
        return out
    for d in sorted(base.iterdir()):
        if not d.is_dir():
            continue
        pj = d / "problem.json"
        if not pj.exists():
            continue
        p = json.loads(pj.read_text())
        sp = solution_path(company, p["frontend_id"], p["title_slug"], root)
        out.append({"frontend_id": p["frontend_id"], "title": p["title"],
                    "title_slug": p["title_slug"], "difficulty": p["difficulty"],
                    "solved": sp.exists()})
    return out


def ensure_solution(company, problem, root=None):
    """题解文件不存在则按模板创建,返回 (路径, created)。"""
    sp = solution_path(company, problem["frontend_id"], problem["title_slug"], root)
    if sp.exists():
        return sp, False
    sp.parent.mkdir(parents=True, exist_ok=True)
    sp.write_text(render.build_solution_template(problem))
    return sp, True
