# LeetCode 企业真题本地刷题系统 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个 Python CLI,从 leetcode.cn 抓取三个秋招学习计划的企业真题固化到本地,支持离线做题与样例对拍判题。

**Architecture:** 单一 Python 包 `oj/`,CLI 入口 `oj.py`。抓取层(cookies+client+fetch)用会员 cookie 一次性把题目落盘为 `problems/`;做题层(store+render+runner)完全离线。题库和题解都提交进 git。

**Tech Stack:** Python 3.12,`requests`(GraphQL),`pycryptodome`(解密 Edge cookie),标准库 `sqlite3`/`json`/`importlib`/`argparse`。测试用 `pytest`。

**Spec:** `docs/superpowers/specs/2026-10-01-leetcode-oj-design.md`

## Global Constraints

- Python 3,仅用 `requests` + `pycryptodome` 两个第三方库(HTML→MD 自写精简函数,不引入 html2text)。
- GraphQL endpoint:`https://leetcode.cn/graphql/`。
- 做题/判题层禁止任何网络调用,只读本地 `problems/`。
- cookie 绝不写入题库文件、绝不提交 git;`.env` 在 `.gitignore`。
- 三个计划 planSlug:腾讯 `tencent-2023-fall-sprint`、字节 `bytedance-2023-fall-sprint`、小红书 `xiaohongshu-2023-fall-sprint`;短名 `tencent`/`bytedance`/`xiaohongshu`。
- 题目目录命名:`problems/<公司>/<4位补零编号>.<titleSlug>/`,题解:`solutions/<公司>/<4位补零编号>.<titleSlug>.py`。
- python3 模板取 `codeSnippets` 中 `langSlug == "python3"`。

---

## File Structure

- `oj/__init__.py` — 空包标记
- `oj/config.py` — 常量:计划映射、endpoint、仓库根路径解析
- `oj/cookies.py` — 从 Edge 读取并解密 leetcode.cn 的 cookie,`.env` 兜底
- `oj/client.py` — GraphQL 客户端:`study_plan_detail`、`question_detail`
- `oj/render.py` — HTML→Markdown、生成 Python 题解模板
- `oj/store.py` — 题库/题解路径解析、落盘、列目录、完成状态
- `oj/runner.py` — 本地判题:动态加载题解 + 样例对拍
- `oj/fetch.py` — 抓取编排
- `oj.py` — argparse CLI,分发到各命令
- `tests/` — pytest 测试(runner/render/store/config 为主,无网络)
- `requirements.txt`、`.gitignore`、`.env.example`、`README.md`

---

### Task 1: 项目骨架与配置

**Files:**
- Create: `oj/__init__.py`、`oj/config.py`、`requirements.txt`、`.gitignore`、`.env.example`、`tests/__init__.py`、`tests/test_config.py`

**Interfaces:**
- Produces:
  - `oj.config.PLANS: dict[str, dict]` — 短名→`{"slug": str, "name": str}`,键为 `tencent`/`bytedance`/`xiaohongshu`
  - `oj.config.GRAPHQL_URL: str`
  - `oj.config.REPO_ROOT: pathlib.Path` — 仓库根(= 本文件上溯两级)
  - `oj.config.PROBLEMS_DIR: Path`、`oj.config.SOLUTIONS_DIR: Path`
  - `oj.config.company_slug(short: str) -> str` — 短名→planSlug,未知短名抛 `KeyError`
  - `oj.config.pad_id(frontend_id: str|int) -> str` — 补零 4 位,如 `"1"`→`"0001"`

- [ ] **Step 1: 写失败测试** `tests/test_config.py`

```python
from oj import config

def test_company_slug_known():
    assert config.company_slug("tencent") == "tencent-2023-fall-sprint"
    assert config.company_slug("bytedance") == "bytedance-2023-fall-sprint"
    assert config.company_slug("xiaohongshu") == "xiaohongshu-2023-fall-sprint"

def test_pad_id():
    assert config.pad_id(1) == "0001"
    assert config.pad_id("42") == "0042"
    assert config.pad_id(12345) == "12345"

def test_graphql_url():
    assert config.GRAPHQL_URL == "https://leetcode.cn/graphql/"

def test_dirs_under_repo_root():
    assert config.PROBLEMS_DIR == config.REPO_ROOT / "problems"
    assert config.SOLUTIONS_DIR == config.REPO_ROOT / "solutions"
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd ~/leetcode-oj/.claude/worktrees/leetcode-oj-build && python -m pytest tests/test_config.py -v`
Expected: FAIL(`ModuleNotFoundError: oj` 或 AttributeError)

- [ ] **Step 3: 写实现** `oj/__init__.py`(空文件)、`tests/__init__.py`(空文件)、`oj/config.py`

```python
# oj/config.py
from pathlib import Path

GRAPHQL_URL = "https://leetcode.cn/graphql/"
REPO_ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = REPO_ROOT / "problems"
SOLUTIONS_DIR = REPO_ROOT / "solutions"

PLANS = {
    "tencent": {"slug": "tencent-2023-fall-sprint", "name": "腾讯秋招高效备战"},
    "bytedance": {"slug": "bytedance-2023-fall-sprint", "name": "字节跳动秋招心动计划"},
    "xiaohongshu": {"slug": "xiaohongshu-2023-fall-sprint", "name": "小红书秋招特训计划"},
}

def company_slug(short: str) -> str:
    return PLANS[short]["slug"]

def pad_id(frontend_id) -> str:
    return str(frontend_id).zfill(4)
```

- [ ] **Step 4: 写 requirements.txt / .gitignore / .env.example**

`requirements.txt`:
```
requests>=2.31
pycryptodome>=3.19
pytest>=8.0
```

`.gitignore`:
```
.env
__pycache__/
*.pyc
.pytest_cache/
.claude/
```

`.env.example`:
```
# 仅当从 Edge 自动读取 cookie 失败时,手动填这两个值(浏览器开发者工具 Application→Cookies→leetcode.cn)
LEETCODE_SESSION=
LEETCODE_CSRFTOKEN=
```

- [ ] **Step 5: 运行测试确认通过**

Run: `python -m pytest tests/test_config.py -v`
Expected: PASS(4 passed)

- [ ] **Step 6: 提交**

```bash
git add oj tests requirements.txt .gitignore .env.example
git commit -m "feat: 项目骨架与配置(计划映射、路径、补零)"
```

---

### Task 2: HTML→Markdown 与题解模板生成

**Files:**
- Create: `oj/render.py`、`tests/test_render.py`

**Interfaces:**
- Consumes: 无
- Produces:
  - `oj.render.html_to_markdown(html: str) -> str` — 轻量转换 `<pre>/<code>/<b>/<strong>/<ul>/<li>/<p>/<sup>/<sub>/<br>` 等,去标签,还原 `&lt;&gt;&amp;&nbsp;` 实体
  - `oj.render.build_solution_template(problem: dict) -> str` — 由 problem.json 结构生成 Python 题解文件文本:顶部注释(题号/标题/难度/url)+ `codeSnippet` 原样插入;若无 snippet 则按 `metaData` 造一个 `class Solution:` 骨架

- [ ] **Step 1: 写失败测试** `tests/test_render.py`

```python
from oj import render

def test_html_to_markdown_basic():
    html = "<p>给定&nbsp;<code>nums</code>&nbsp;数组&lt;x&gt;</p>"
    md = render.html_to_markdown(html)
    assert "nums" in md
    assert "&nbsp;" not in md and "&lt;" not in md
    assert "<x>" in md  # 实体已还原

def test_html_to_markdown_pre_block():
    html = "<pre>输入: nums = [2,7]\n输出: [0,1]</pre>"
    md = render.html_to_markdown(html)
    assert "nums = [2,7]" in md

def test_build_solution_template_uses_snippet():
    problem = {
        "frontend_id": "1", "title": "两数之和", "title_slug": "two-sum",
        "difficulty": "EASY", "url": "https://leetcode.cn/problems/two-sum/",
        "code_snippet": "class Solution:\n    def twoSum(self, nums, target):\n        ",
        "meta": {"name": "twoSum", "params": [{"name": "nums", "type": "integer[]"}], "return": {"type": "integer[]"}},
    }
    text = render.build_solution_template(problem)
    assert "class Solution:" in text
    assert "def twoSum" in text
    assert "两数之和" in text and "two-sum" in text
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_render.py -v`
Expected: FAIL(`AttributeError: module 'oj.render'`)

- [ ] **Step 3: 写实现** `oj/render.py`

```python
import re, html as _html

_TAG = re.compile(r"<[^>]+>")

def html_to_markdown(html: str) -> str:
    if not html:
        return ""
    s = html
    s = re.sub(r"<\s*br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</\s*p\s*>", "\n\n", s, flags=re.I)
    s = re.sub(r"<\s*li\s*>", "- ", s, flags=re.I)
    s = re.sub(r"</\s*li\s*>", "\n", s, flags=re.I)
    s = re.sub(r"</?\s*(b|strong)\s*>", "**", s, flags=re.I)
    s = re.sub(r"<\s*pre\s*>", "\n```\n", s, flags=re.I)
    s = re.sub(r"</\s*pre\s*>", "\n```\n", s, flags=re.I)
    s = re.sub(r"<\s*sup\s*>", "^", s, flags=re.I)
    s = re.sub(r"<\s*sub\s*>", "_", s, flags=re.I)
    s = _TAG.sub("", s)            # 去掉剩余标签
    s = _html.unescape(s)          # 还原 &lt; &gt; &amp; &nbsp; 等
    s = s.replace("\xa0", " ")
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def build_solution_template(problem: dict) -> str:
    header = (
        f'# {problem.get("frontend_id","")}. {problem.get("title","")}'
        f'  [{problem.get("difficulty","")}]\n'
        f'# {problem.get("url","")}\n\n'
    )
    snippet = problem.get("code_snippet")
    if snippet:
        return header + snippet.rstrip() + "\n"
    meta = problem.get("meta") or {}
    name = meta.get("name", "solve")
    params = ", ".join(p["name"] for p in meta.get("params", []))
    sig = f"self, {params}" if params else "self"
    return header + f"class Solution:\n    def {name}({sig}):\n        pass\n"
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/test_render.py -v`
Expected: PASS(3 passed)

- [ ] **Step 5: 提交**

```bash
git add oj/render.py tests/test_render.py
git commit -m "feat: 题干 HTML→Markdown 与 Python 题解模板生成"
```

---

### Task 3: 本地判题 runner(核心,TDD 重点)

**Files:**
- Create: `oj/runner.py`、`tests/test_runner.py`、`tests/fixtures/`(测试夹具题库)

**Interfaces:**
- Consumes: 无(直接读文件系统)
- Produces:
  - `oj.runner.parse_inputs(raw: str, params: list[dict]) -> list[list]` — 把 `exampleTestcases`(每 len(params) 行为一组,每行一个 JSON)切成多组实参列表
  - `oj.runner.normalize(value) -> any` — 判等归一化:浮点保留容差标记交由 compare 处理;此函数负责 list/dict 递归转可比较结构
  - `oj.runner.compare(expected, actual) -> bool` — 深比较,浮点容差 1e-5
  - `oj.runner.run_solution(solution_path: str, problem: dict) -> dict` — 返回 `{"passed": int, "total": int, "ac": bool, "cases": [{"ok": bool, "input": ..., "expected": ..., "got": ...}]}`;加载失败/运行异常时该用例 `ok=False` 并带 `error`

**判题调用约定(关键):** `problem["meta"]["name"]` 是方法名;`parse_inputs` 产出的每组实参按 `params` 顺序传给 `Solution().<name>(*args)`;期望输出来自 `testcases.json` 的 `expected` 列表(与输入组一一对应)。

- [ ] **Step 1: 写失败测试 + 夹具** `tests/test_runner.py`

```python
import json, os, textwrap
from pathlib import Path
from oj import runner

def test_parse_inputs_two_params():
    raw = "[2,7,11,15]\n9\n[3,2,4]\n6"
    params = [{"name": "nums", "type": "integer[]"}, {"name": "target", "type": "integer"}]
    groups = runner.parse_inputs(raw, params)
    assert groups == [[[2,7,11,15], 9], [[3,2,4], 6]]

def test_compare_float_tolerance():
    assert runner.compare(1.0, 1.0 + 1e-7) is True
    assert runner.compare([1,2], [1,2]) is True
    assert runner.compare([1,2], [2,1]) is False

def test_run_solution_ac(tmp_path):
    # 造一个 two-sum 题库 + 正确题解,跑通判 AC
    sol = tmp_path / "sol.py"
    sol.write_text(textwrap.dedent('''
        class Solution:
            def twoSum(self, nums, target):
                seen = {}
                for i, n in enumerate(nums):
                    if target - n in seen:
                        return [seen[target - n], i]
                    seen[n] = i
    '''))
    problem = {
        "meta": {"name": "twoSum", "params": [{"name":"nums","type":"integer[]"},{"name":"target","type":"integer"}]},
        "testcases": {
            "raw": "[2,7,11,15]\n9\n[3,2,4]\n6",
            "expected": [[0,1], [1,2]],
        },
    }
    result = runner.run_solution(str(sol), problem)
    assert result["ac"] is True
    assert result["passed"] == 2 and result["total"] == 2

def test_run_solution_wa(tmp_path):
    sol = tmp_path / "sol.py"
    sol.write_text("class Solution:\n    def twoSum(self, nums, target):\n        return [9,9]\n")
    problem = {
        "meta": {"name": "twoSum", "params": [{"name":"nums","type":"integer[]"},{"name":"target","type":"integer"}]},
        "testcases": {"raw": "[2,7,11,15]\n9", "expected": [[0,1]]},
    }
    result = runner.run_solution(str(sol), problem)
    assert result["ac"] is False
    assert result["cases"][0]["ok"] is False
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_runner.py -v`
Expected: FAIL(`AttributeError`)

- [ ] **Step 3: 写实现** `oj/runner.py`

```python
import json, importlib.util, math

def parse_inputs(raw: str, params: list) -> list:
    n = len(params) or 1
    lines = [ln for ln in (raw or "").splitlines() if ln.strip() != ""]
    groups = []
    for i in range(0, len(lines), n):
        chunk = lines[i:i+n]
        if len(chunk) < n:
            break
        groups.append([json.loads(x) for x in chunk])
    return groups

def compare(expected, actual) -> bool:
    if isinstance(expected, float) or isinstance(actual, float):
        try:
            return math.isclose(float(expected), float(actual), rel_tol=1e-5, abs_tol=1e-5)
        except (TypeError, ValueError):
            return expected == actual
    if isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            return False
        return all(compare(a, b) for a, b in zip(expected, actual))
    if isinstance(expected, dict) and isinstance(actual, dict):
        if expected.keys() != actual.keys():
            return False
        return all(compare(expected[k], actual[k]) for k in expected)
    return expected == actual

def normalize(value):
    return value  # 预留:复杂题型归一化;首版直通

def _load_solution(path: str):
    spec = importlib.util.spec_from_file_location("_sol", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.Solution()

def run_solution(solution_path: str, problem: dict) -> dict:
    meta = problem["meta"]
    name = meta["name"]
    params = meta.get("params", [])
    tc = problem["testcases"]
    groups = parse_inputs(tc.get("raw", ""), params)
    expected = tc.get("expected", [])
    cases = []
    try:
        sol = _load_solution(solution_path)
        method = getattr(sol, name)
    except Exception as e:  # 加载失败:全部用例判错
        for i, args in enumerate(groups):
            cases.append({"ok": False, "input": args,
                          "expected": expected[i] if i < len(expected) else None,
                          "got": None, "error": f"load error: {e}"})
        return {"passed": 0, "total": len(groups), "ac": len(groups) == 0, "cases": cases}
    passed = 0
    for i, args in enumerate(groups):
        exp = expected[i] if i < len(expected) else None
        try:
            got = method(*[json.loads(json.dumps(a)) for a in args])
            ok = compare(exp, got)
        except Exception as e:
            got, ok = None, False
            cases.append({"ok": False, "input": args, "expected": exp, "got": None, "error": str(e)})
            continue
        if ok:
            passed += 1
        cases.append({"ok": ok, "input": args, "expected": exp, "got": got})
    total = len(groups)
    return {"passed": passed, "total": total, "ac": total > 0 and passed == total, "cases": cases}
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/test_runner.py -v`
Expected: PASS(4 passed)

- [ ] **Step 5: 提交**

```bash
git add oj/runner.py tests/test_runner.py
git commit -m "feat: 本地判题 runner(样例对拍、浮点容差、异常兜底)"
```

---

### Task 4: store 题库/题解读写与路径

**Files:**
- Create: `oj/store.py`、`tests/test_store.py`

**Interfaces:**
- Consumes: `oj.config`(PROBLEMS_DIR/SOLUTIONS_DIR/pad_id)、`oj.render.build_solution_template`
- Produces:
  - `oj.store.problem_dir(company, frontend_id, title_slug) -> Path`
  - `oj.store.solution_path(company, frontend_id, title_slug) -> Path`
  - `oj.store.save_problem(company, problem: dict) -> Path` — 写 `problem.json`+`testcases.json`+`README.md`,返回题目目录
  - `oj.store.load_problem(company, key: str) -> dict` — key 为 titleSlug 或题号;读回合并后的 problem dict(含 testcases、meta)
  - `oj.store.list_problems(company) -> list[dict]` — 列出 `{frontend_id,title,title_slug,difficulty,solved}`,solved=solutions 下文件存在
  - `oj.store.ensure_solution(company, problem) -> tuple[Path, bool]` — 不存在则用模板创建,返回 (路径, created)
  - 根目录可注入(测试用):各函数接受可选 `root: Path=None`,默认 `config.REPO_ROOT`

- [ ] **Step 1: 写失败测试** `tests/test_store.py`

```python
from oj import store

PROBLEM = {
    "frontend_id": "1", "title": "两数之和", "title_slug": "two-sum",
    "difficulty": "EASY", "url": "https://leetcode.cn/problems/two-sum/",
    "content_md": "给定数组…", "code_snippet": "class Solution:\n    def twoSum(self, nums, target):\n        pass",
    "meta": {"name": "twoSum", "params": [{"name":"nums","type":"integer[]"}], "return": {"type":"integer[]"}},
    "testcases": {"raw": "[2,7,11,15]\n9", "expected": [[0,1]]},
}

def test_save_and_load_problem(tmp_path):
    store.save_problem("tencent", PROBLEM, root=tmp_path)
    loaded = store.load_problem("tencent", "two-sum", root=tmp_path)
    assert loaded["title"] == "两数之和"
    assert loaded["testcases"]["expected"] == [[0,1]]
    assert (tmp_path / "problems" / "tencent" / "0001.two-sum" / "README.md").exists()

def test_list_problems_solved_flag(tmp_path):
    store.save_problem("tencent", PROBLEM, root=tmp_path)
    items = store.list_problems("tencent", root=tmp_path)
    assert items and items[0]["title_slug"] == "two-sum"
    assert items[0]["solved"] is False
    path, created = store.ensure_solution("tencent", PROBLEM, root=tmp_path)
    assert created is True and path.exists()
    items2 = store.list_problems("tencent", root=tmp_path)
    assert items2[0]["solved"] is True

def test_load_problem_by_id(tmp_path):
    store.save_problem("tencent", PROBLEM, root=tmp_path)
    loaded = store.load_problem("tencent", "1", root=tmp_path)
    assert loaded["title_slug"] == "two-sum"
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_store.py -v`
Expected: FAIL

- [ ] **Step 3: 写实现** `oj/store.py`

```python
import json
from pathlib import Path
from oj import config, render

def _root(root): return Path(root) if root else config.REPO_ROOT
def _problems(root): return _root(root) / "problems"
def _solutions(root): return _root(root) / "solutions"

def _dirname(frontend_id, title_slug): return f"{config.pad_id(frontend_id)}.{title_slug}"

def problem_dir(company, frontend_id, title_slug, root=None):
    return _problems(root) / company / _dirname(frontend_id, title_slug)

def solution_path(company, frontend_id, title_slug, root=None):
    return _solutions(root) / company / f"{_dirname(frontend_id, title_slug)}.py"

def save_problem(company, problem, root=None):
    d = problem_dir(company, problem["frontend_id"], problem["title_slug"], root)
    d.mkdir(parents=True, exist_ok=True)
    meta_doc = {k: problem[k] for k in
                ("frontend_id","title","title_slug","difficulty","url","meta","code_snippet")
                if k in problem}
    (d / "problem.json").write_text(json.dumps(meta_doc, ensure_ascii=False, indent=2))
    (d / "testcases.json").write_text(json.dumps(problem["testcases"], ensure_ascii=False, indent=2))
    title = f'# {problem["frontend_id"]}. {problem["title"]}  [{problem["difficulty"]}]\n\n'
    (d / "README.md").write_text(title + problem.get("content_md","") + "\n")
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
    d = _find_dir(company, key, root)
    problem = json.loads((d / "problem.json").read_text())
    problem["testcases"] = json.loads((d / "testcases.json").read_text())
    return problem

def list_problems(company, root=None):
    base = _problems(root) / company
    out = []
    if not base.exists():
        return out
    for d in sorted(base.iterdir()):
        if not d.is_dir():
            continue
        p = json.loads((d / "problem.json").read_text())
        sp = solution_path(company, p["frontend_id"], p["title_slug"], root)
        out.append({"frontend_id": p["frontend_id"], "title": p["title"],
                    "title_slug": p["title_slug"], "difficulty": p["difficulty"],
                    "solved": sp.exists()})
    return out

def ensure_solution(company, problem, root=None):
    sp = solution_path(company, problem["frontend_id"], problem["title_slug"], root)
    if sp.exists():
        return sp, False
    sp.parent.mkdir(parents=True, exist_ok=True)
    sp.write_text(render.build_solution_template(problem))
    return sp, True
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/test_store.py -v`
Expected: PASS(3 passed)

- [ ] **Step 5: 提交**

```bash
git add oj/store.py tests/test_store.py
git commit -m "feat: store 题库/题解读写、路径解析、完成状态"
```

---

### Task 5: cookies.py 从 Edge 读取 cookie

**Files:**
- Create: `oj/cookies.py`、`tests/test_cookies.py`

**Interfaces:**
- Consumes: 无
- Produces:
  - `oj.cookies.get_leetcode_cookies() -> dict` — 返回 `{"LEETCODE_SESSION": str, "csrftoken": str}`;优先 Edge,失败回退 `.env`;都没有则抛 `RuntimeError` 带指引
  - `oj.cookies.from_env() -> dict | None` — 读 `.env`(或环境变量)里的 `LEETCODE_SESSION`/`LEETCODE_CSRFTOKEN`
  - `oj.cookies.decrypt_chromium_value(encrypted: bytes, key: bytes) -> str` — AES-128-CBC(v10 前缀)解密单个值

**说明:** Edge 读取涉及钥匙串与本机路径,无法在 CI 稳定测试;单测只覆盖 `from_env` 和 `decrypt_chromium_value`(用已知 key+密文的往返构造),Edge 整链路在 Task 7 真实验证。

- [ ] **Step 1: 写失败测试** `tests/test_cookies.py`

```python
import os
from oj import cookies

def test_from_env(monkeypatch):
    monkeypatch.setenv("LEETCODE_SESSION", "sess123")
    monkeypatch.setenv("LEETCODE_CSRFTOKEN", "csrf456")
    c = cookies.from_env()
    assert c == {"LEETCODE_SESSION": "sess123", "csrftoken": "csrf456"}

def test_from_env_missing(monkeypatch):
    monkeypatch.delenv("LEETCODE_SESSION", raising=False)
    monkeypatch.delenv("LEETCODE_CSRFTOKEN", raising=False)
    assert cookies.from_env() is None

def test_decrypt_roundtrip():
    # 用与实现相同的 KDF 造一段 v10 密文,验证能解回明文
    from Crypto.Cipher import AES
    from Crypto.Protocol.KDF import PBKDF2
    from Crypto.Hash import SHA1
    key = PBKDF2(b"peanuts", b"saltysalt", 16, count=1003, hmac_hash_module=SHA1)
    iv = b" " * 16
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plain = b"hello-session-value"
    pad = 16 - len(plain) % 16
    enc = b"v10" + cipher.encrypt(plain + bytes([pad]) * pad)
    assert cookies.decrypt_chromium_value(enc, key) == "hello-session-value"
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_cookies.py -v`
Expected: FAIL

- [ ] **Step 3: 写实现** `oj/cookies.py`

```python
import os, sqlite3, shutil, subprocess, tempfile
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA1

EDGE_COOKIES = Path.home() / "Library/Application Support/Microsoft Edge/Default/Cookies"
KEYCHAIN_SERVICE = "Microsoft Edge Safe Storage"

def from_env():
    # 优先读 .env 文件,再读环境变量
    env = {}
    envfile = Path(__file__).resolve().parent.parent / ".env"
    if envfile.exists():
        for line in envfile.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    sess = env.get("LEETCODE_SESSION") or os.environ.get("LEETCODE_SESSION")
    csrf = env.get("LEETCODE_CSRFTOKEN") or os.environ.get("LEETCODE_CSRFTOKEN")
    if sess and csrf:
        return {"LEETCODE_SESSION": sess, "csrftoken": csrf}
    return None

def _keychain_password():
    out = subprocess.check_output(
        ["security", "find-generic-password", "-wa", KEYCHAIN_SERVICE],
        stderr=subprocess.DEVNULL)
    return out.strip()

def decrypt_chromium_value(encrypted: bytes, key: bytes) -> str:
    if encrypted[:3] in (b"v10", b"v11"):
        encrypted = encrypted[3:]
    iv = b" " * 16
    cipher = AES.new(key, AES.MODE_CBC, iv)
    dec = cipher.decrypt(encrypted)
    pad = dec[-1]
    dec = dec[:-pad] if 0 < pad <= 16 else dec
    # 新版 Chromium 在明文前有 32 字节 SHA256 域哈希前缀;若存在则剥离
    try:
        return dec.decode("utf-8")
    except UnicodeDecodeError:
        return dec[32:].decode("utf-8", errors="replace")

def _from_edge():
    if not EDGE_COOKIES.exists():
        return None
    passwd = _keychain_password()
    key = PBKDF2(passwd, b"saltysalt", 16, count=1003, hmac_hash_module=SHA1)
    tmp = Path(tempfile.gettempdir()) / "edge_cookies_copy.sqlite"
    shutil.copy2(EDGE_COOKIES, tmp)  # 避免 Edge 占用锁
    con = sqlite3.connect(str(tmp))
    rows = con.execute(
        "SELECT name, encrypted_value FROM cookies WHERE host_key LIKE '%leetcode.cn%'"
    ).fetchall()
    con.close()
    out = {}
    for name, enc in rows:
        if name in ("LEETCODE_SESSION", "csrftoken"):
            try:
                out[name] = decrypt_chromium_value(enc, key)
            except Exception:
                pass
    if out.get("LEETCODE_SESSION") and out.get("csrftoken"):
        return out
    return None

def get_leetcode_cookies() -> dict:
    try:
        c = _from_edge()
    except Exception:
        c = None
    if c:
        return c
    c = from_env()
    if c:
        return c
    raise RuntimeError(
        "无法获取 leetcode.cn 登录 cookie。\n"
        "请确认已在 Edge 登录 leetcode.cn,或手动在 .env 填 "
        "LEETCODE_SESSION 和 LEETCODE_CSRFTOKEN(浏览器开发者工具 → Application → Cookies)。")
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/test_cookies.py -v`
Expected: PASS(3 passed)

- [ ] **Step 5: 提交**

```bash
git add oj/cookies.py tests/test_cookies.py
git commit -m "feat: 从 Edge 读取并解密 leetcode.cn cookie(.env 兜底)"
```

---

### Task 6: client.py GraphQL 客户端

**Files:**
- Create: `oj/client.py`、`tests/test_client.py`

**Interfaces:**
- Consumes: `oj.config.GRAPHQL_URL`
- Produces:
  - `oj.client.LeetCodeClient(cookies: dict|None)` — 构造持有 session
  - `.post(query: str, variables: dict, operation_name: str) -> dict` — 返回 `data`;HTTP/GraphQL error 抛 `RuntimeError`
  - `.study_plan_detail(plan_slug: str) -> list[dict]` — 返回题目列表 `[{title_slug,frontend_id,title,translated_title,difficulty,paid_only}]`(从 planSubGroups 扁平化)
  - `.question_detail(title_slug: str) -> dict` — 返回 `{frontend_id,title,title_slug,difficulty,url,content_html,code_snippet,meta(dict),example_testcases(str),sample_testcase(str)}`

**说明:** 不打真实网络的单测:用 monkeypatch 替换 `.post` 返回固定 GraphQL 响应,验证解析逻辑正确。真实网络在 Task 7。

- [ ] **Step 1: 写失败测试** `tests/test_client.py`

```python
from oj import client

def test_study_plan_detail_flatten(monkeypatch):
    fake = {"studyPlanV2Detail": {"planSubGroups": [
        {"questions": [
            {"titleSlug":"two-sum","questionFrontendId":"1","title":"Two Sum",
             "translatedTitle":"两数之和","difficulty":"EASY","paidOnly":False}]},
        {"questions": [
            {"titleSlug":"add-two-numbers","questionFrontendId":"2","title":"Add",
             "translatedTitle":"两数相加","difficulty":"MEDIUM","paidOnly":True}]},
    ]}}
    c = client.LeetCodeClient(None)
    monkeypatch.setattr(c, "post", lambda *a, **k: fake)
    qs = c.study_plan_detail("tencent-2023-fall-sprint")
    assert [q["title_slug"] for q in qs] == ["two-sum","add-two-numbers"]
    assert qs[0]["frontend_id"] == "1"

def test_question_detail_parse(monkeypatch):
    fake = {"question": {
        "questionFrontendId":"1","title":"Two Sum","titleSlug":"two-sum",
        "translatedTitle":"两数之和","difficulty":"Easy","isPaidOnly":False,
        "translatedContent":"<p>给定…</p>",
        "codeSnippets":[{"langSlug":"python","code":"old"},
                        {"langSlug":"python3","code":"class Solution:\n    def twoSum(self): pass"}],
        "sampleTestCase":"[2,7,11,15]\n9",
        "exampleTestcases":"[2,7,11,15]\n9\n[3,2,4]\n6",
        "metaData":"{\"name\":\"twoSum\",\"params\":[{\"name\":\"nums\",\"type\":\"integer[]\"}],\"return\":{\"type\":\"integer[]\"}}",
    }}
    c = client.LeetCodeClient(None)
    monkeypatch.setattr(c, "post", lambda *a, **k: fake)
    d = c.question_detail("two-sum")
    assert d["code_snippet"].startswith("class Solution")  # 选中 python3 而非 python
    assert d["meta"]["name"] == "twoSum"
    assert d["example_testcases"].count("\n") == 3
    assert d["url"] == "https://leetcode.cn/problems/two-sum/"
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_client.py -v`
Expected: FAIL

- [ ] **Step 3: 写实现** `oj/client.py`

```python
import json, time, requests
from oj import config

_PLAN_QUERY = """
query studyPlanV2Detail($planSlug: String!) {
  studyPlanV2Detail(planSlug: $planSlug) {
    slug name premiumOnly questionNum
    planSubGroups { name questionNum
      questions { titleSlug questionFrontendId title translatedTitle difficulty paidOnly } } } }
"""

_QUESTION_QUERY = """
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionFrontendId title titleSlug translatedTitle difficulty isPaidOnly
    translatedContent content
    codeSnippets { lang langSlug code }
    sampleTestCase exampleTestcases metaData } }
"""

class LeetCodeClient:
    def __init__(self, cookies: dict | None):
        self.s = requests.Session()
        self.cookies = cookies or {}
        self.s.headers.update({
            "Content-Type": "application/json",
            "Origin": "https://leetcode.cn",
            "Referer": "https://leetcode.cn/",
            "User-Agent": "Mozilla/5.0 leetcode-oj",
        })
        if self.cookies:
            self.s.headers["x-csrftoken"] = self.cookies.get("csrftoken", "")
            self.s.headers["Cookie"] = "; ".join(f"{k}={v}" for k, v in self.cookies.items())

    def post(self, query, variables, operation_name):
        r = self.s.post(config.GRAPHQL_URL,
                        json={"query": query, "variables": variables, "operationName": operation_name},
                        timeout=30)
        r.raise_for_status()
        body = r.json()
        if body.get("errors"):
            raise RuntimeError(f"GraphQL error: {body['errors']}")
        return body["data"]

    def study_plan_detail(self, plan_slug):
        data = self.post(_PLAN_QUERY, {"planSlug": plan_slug}, "studyPlanV2Detail")
        detail = data.get("studyPlanV2Detail") or {}
        out = []
        for grp in detail.get("planSubGroups") or []:
            for q in grp.get("questions") or []:
                out.append({
                    "title_slug": q["titleSlug"], "frontend_id": q["questionFrontendId"],
                    "title": q.get("title"), "translated_title": q.get("translatedTitle"),
                    "difficulty": q.get("difficulty"), "paid_only": q.get("paidOnly"),
                })
        return out

    def question_detail(self, title_slug):
        data = self.post(_QUESTION_QUERY, {"titleSlug": title_slug}, "questionData")
        q = data.get("question") or {}
        snippet = ""
        for cs in q.get("codeSnippets") or []:
            if cs.get("langSlug") == "python3":
                snippet = cs["code"]; break
        meta = json.loads(q["metaData"]) if q.get("metaData") else {}
        return {
            "frontend_id": q.get("questionFrontendId"), "title": q.get("translatedTitle") or q.get("title"),
            "title_slug": q.get("titleSlug") or title_slug, "difficulty": q.get("difficulty"),
            "url": f"https://leetcode.cn/problems/{title_slug}/",
            "content_html": q.get("translatedContent") or q.get("content") or "",
            "code_snippet": snippet, "meta": meta,
            "example_testcases": q.get("exampleTestcases") or "",
            "sample_testcase": q.get("sampleTestCase") or "",
        }
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/test_client.py -v`
Expected: PASS(2 passed)

- [ ] **Step 5: 提交**

```bash
git add oj/client.py tests/test_client.py
git commit -m "feat: leetcode.cn GraphQL 客户端(计划详情、单题详情解析)"
```

---

### Task 7: fetch.py 抓取编排 + 真实验证

**Files:**
- Create: `oj/fetch.py`、`tests/test_fetch.py`

**Interfaces:**
- Consumes: `oj.cookies.get_leetcode_cookies`、`oj.client.LeetCodeClient`、`oj.store.save_problem`、`oj.render.html_to_markdown`
- Produces:
  - `oj.fetch.build_problem(detail: dict) -> dict` — 把 `client.question_detail` 结果转成 `store.save_problem` 所需结构(含 `content_md`、`testcases={"raw","expected"}`)。`expected` 从 `example_testcases` 无法可靠反推(LeetCode 不单独给期望输出),首版策略:`expected` 置为空列表并在 README 注明需用户补;`raw` 存 `example_testcases`
  - `oj.fetch.fetch_company(short: str, client=None, delay=1.0) -> int` — 抓一个公司,返回题目数;client 可注入(测试)

**关键设计决定(expected 来源):** LeetCode 的 `exampleTestcases` 只有输入、没有期望输出。因此判题的 `expected` 需要从题干 Example 里解析或由用户补。首版:`build_problem` 尝试从 `content_html` 的 Example 块正则抽取 `输出:`/`Output:` 后的值作为 `expected`;抽取不到则留空列表,README 提示手工补。此解析在 `fetch.extract_expected(content_html: str) -> list` 中实现并单测。

- [ ] **Step 1: 写失败测试** `tests/test_fetch.py`

```python
from oj import fetch

def test_extract_expected_cn():
    html = ("<p>示例 1:</p><pre>输入:nums = [2,7,11,15], target = 9\n输出:[0,1]</pre>"
            "<p>示例 2:</p><pre>输入:nums = [3,2,4], target = 6\n输出:[1,2]</pre>")
    assert fetch.extract_expected(html) == [[0,1],[1,2]]

def test_build_problem_shape():
    detail = {
        "frontend_id":"1","title":"两数之和","title_slug":"two-sum","difficulty":"EASY",
        "url":"https://leetcode.cn/problems/two-sum/",
        "content_html":"<pre>输入:nums=[2,7], target=9\n输出:[0,1]</pre>",
        "code_snippet":"class Solution:\n    def twoSum(self): pass",
        "meta":{"name":"twoSum","params":[{"name":"nums","type":"integer[]"}],"return":{"type":"integer[]"}},
        "example_testcases":"[2,7]\n9", "sample_testcase":"[2,7]\n9",
    }
    p = fetch.build_problem(detail)
    assert p["testcases"]["raw"] == "[2,7]\n9"
    assert p["testcases"]["expected"] == [[0,1]]
    assert "content_md" in p and "<pre>" not in p["content_md"]

def test_fetch_company_uses_client(monkeypatch, tmp_path):
    from oj import store
    class FakeClient:
        def study_plan_detail(self, slug):
            return [{"title_slug":"two-sum","frontend_id":"1","difficulty":"EASY"}]
        def question_detail(self, slug):
            return {"frontend_id":"1","title":"两数之和","title_slug":"two-sum","difficulty":"EASY",
                    "url":"u","content_html":"<pre>输出:[0,1]</pre>","code_snippet":"class Solution:\n    pass",
                    "meta":{"name":"twoSum","params":[]}, "example_testcases":"[2,7]\n9","sample_testcase":""}
    monkeypatch.setattr(store, "REPO_ROOT_OVERRIDE", tmp_path, raising=False)
    n = fetch.fetch_company("tencent", client=FakeClient(), delay=0, root=tmp_path)
    assert n == 1
    assert (tmp_path / "problems" / "tencent" / "0001.two-sum" / "problem.json").exists()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_fetch.py -v`
Expected: FAIL

- [ ] **Step 3: 写实现** `oj/fetch.py`

```python
import re, time, html as _html
from oj import config, cookies as cookies_mod, client as client_mod, store, render

_OUT_RE = re.compile(r"(?:输出|Output)\s*[:：]\s*(.+)")

def extract_expected(content_html: str) -> list:
    text = _html.unescape(re.sub(r"<[^>]+>", "\n", content_html or ""))
    out = []
    for m in _OUT_RE.finditer(text):
        raw = m.group(1).strip()
        raw = raw.split("\n")[0].strip().rstrip("。.")
        try:
            import json
            out.append(json.loads(raw))
        except Exception:
            # 退化:去掉引号的字符串
            out.append(raw.strip('"'))
    return out

def build_problem(detail: dict) -> dict:
    expected = extract_expected(detail.get("content_html", ""))
    return {
        "frontend_id": detail["frontend_id"], "title": detail["title"],
        "title_slug": detail["title_slug"], "difficulty": detail["difficulty"],
        "url": detail["url"], "meta": detail.get("meta", {}),
        "code_snippet": detail.get("code_snippet", ""),
        "content_md": render.html_to_markdown(detail.get("content_html", "")),
        "testcases": {"raw": detail.get("example_testcases", ""), "expected": expected},
    }

def fetch_company(short: str, client=None, delay: float = 1.0, root=None) -> int:
    if client is None:
        c = cookies_mod.get_leetcode_cookies()
        client = client_mod.LeetCodeClient(c)
    plan_slug = config.company_slug(short)
    questions = client.study_plan_detail(plan_slug)
    if not questions:
        raise RuntimeError(
            f"{short}: 题目列表为空。该计划为会员专属,请确认 Edge 已登录 leetcode.cn 会员账号。")
    count = 0
    for q in questions:
        detail = client.question_detail(q["title_slug"])
        problem = build_problem(detail)
        store.save_problem(short, problem, root=root)
        count += 1
        print(f"  [{count}/{len(questions)}] {problem['frontend_id']}. {problem['title']}")
        if delay:
            time.sleep(delay)
    return count
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/test_fetch.py -v`
Expected: PASS(3 passed)

- [ ] **Step 5: 全量单测**

Run: `python -m pytest -v`
Expected: 全部 PASS

- [ ] **Step 6: 提交**

```bash
git add oj/fetch.py tests/test_fetch.py
git commit -m "feat: 抓取编排(计划→题目→落盘,从题干抽取期望输出)"
```

- [ ] **Step 7: 真实验证(需 Edge 登录态,人工触发点)**

此步依赖用户 Edge 登录态,放到 Task 9 CLI 完成后统一实抓(见 Task 9 Step)。此处仅标记:fetch 逻辑已就绪,待 CLI 组装后跑真实 `fetch tencent`。

---

### Task 8: oj.py CLI 组装

**Files:**
- Create: `oj.py`、`tests/test_cli.py`

**Interfaces:**
- Consumes: 全部 `oj.*` 模块
- Produces: 可执行 CLI,子命令 `fetch/list/new/test/show`
  - `main(argv: list[str]) -> int` — 便于测试

- [ ] **Step 1: 写失败测试** `tests/test_cli.py`

```python
import sys, textwrap
import oj as _  # noqa
from pathlib import Path
import importlib.util

def _load_cli():
    spec = importlib.util.spec_from_file_location("ojcli", Path(__file__).resolve().parent.parent / "oj.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def test_list_and_test_commands(tmp_path, monkeypatch, capsys):
    from oj import store, config
    monkeypatch.setattr(config, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(config, "PROBLEMS_DIR", tmp_path / "problems")
    monkeypatch.setattr(config, "SOLUTIONS_DIR", tmp_path / "solutions")
    problem = {"frontend_id":"1","title":"两数之和","title_slug":"two-sum","difficulty":"EASY",
               "url":"u","content_md":"题","code_snippet":"class Solution:\n    def twoSum(self,nums,target):\n        seen={}\n        for i,n in enumerate(nums):\n            if target-n in seen: return [seen[target-n],i]\n            seen[n]=i",
               "meta":{"name":"twoSum","params":[{"name":"nums","type":"integer[]"},{"name":"target","type":"integer"}]},
               "testcases":{"raw":"[2,7,11,15]\n9","expected":[[0,1]]}}
    store.save_problem("tencent", problem, root=tmp_path)
    cli = _load_cli()
    assert cli.main(["list","tencent"]) == 0
    assert cli.main(["new","tencent","two-sum"]) == 0
    # 用模板生成的题解此时是空壳,test 应为 WA 或 0;写入正确题解再测
    sp = tmp_path / "solutions" / "tencent" / "0001.two-sum.py"
    sp.write_text(problem["code_snippet"])
    assert cli.main(["test","tencent","two-sum"]) == 0
    out = capsys.readouterr().out
    assert "two-sum" in out or "两数之和" in out
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_cli.py -v`
Expected: FAIL

- [ ] **Step 3: 写实现** `oj.py`

```python
#!/usr/bin/env python3
import argparse, sys
from oj import config, store, runner, render, fetch

def cmd_fetch(args):
    targets = ["tencent","bytedance","xiaohongshu"] if args.company == "all" else [args.company]
    for t in targets:
        print(f"抓取 {config.PLANS[t]['name']} ({config.company_slug(t)}) …")
        n = fetch.fetch_company(t, delay=args.delay)
        print(f"✓ {t}: {n} 题")
    return 0

def cmd_list(args):
    items = store.list_problems(args.company)
    if not items:
        print(f"{args.company}: 暂无题目,先运行 python oj.py fetch {args.company}")
        return 0
    for it in items:
        mark = "✅" if it["solved"] else "⬜"
        print(f"{mark} {config.pad_id(it['frontend_id'])}. {it['title']}  [{it['difficulty']}]  ({it['title_slug']})")
    done = sum(1 for i in items if i["solved"])
    print(f"\n进度:{done}/{len(items)}")
    return 0

def cmd_new(args):
    p = store.load_problem(args.company, args.problem)
    path, created = store.ensure_solution(args.company, p)
    print(("已创建 " if created else "已存在 ") + str(path))
    return 0

def cmd_test(args):
    p = store.load_problem(args.company, args.problem)
    path, _ = store.ensure_solution(args.company, p)
    result = runner.run_solution(str(path), p)
    for i, c in enumerate(result["cases"]):
        tag = "PASS" if c["ok"] else "FAIL"
        print(f"  用例{i+1} {tag}  输入={c['input']}  期望={c['expected']}  实际={c.get('got')}"
              + (f"  错误={c['error']}" if c.get("error") else ""))
    verdict = "AC ✅" if result["ac"] else "WA ❌"
    print(f"\n{p['title']}: {verdict}  ({result['passed']}/{result['total']})")
    if result["total"] == 0:
        print("  注意:该题无本地期望输出(expected 为空),请在 problems/.../testcases.json 补 expected。")
    return 0

def cmd_show(args):
    p = store.load_problem(args.company, args.problem)
    d = store.problem_dir(args.company, p["frontend_id"], p["title_slug"])
    print((d / "README.md").read_text())
    return 0

def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(prog="oj", description="LeetCode 企业真题本地刷题")
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch"); f.add_argument("company"); f.add_argument("--delay", type=float, default=1.0); f.set_defaults(func=cmd_fetch)
    l = sub.add_parser("list"); l.add_argument("company"); l.set_defaults(func=cmd_list)
    n = sub.add_parser("new"); n.add_argument("company"); n.add_argument("problem"); n.set_defaults(func=cmd_new)
    t = sub.add_parser("test"); t.add_argument("company"); t.add_argument("problem"); t.set_defaults(func=cmd_test)
    s = sub.add_parser("show"); s.add_argument("company"); s.add_argument("problem"); s.set_defaults(func=cmd_show)
    args = ap.parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/test_cli.py -v`
Expected: PASS

- [ ] **Step 5: 全量单测**

Run: `python -m pytest -v`
Expected: 全部 PASS

- [ ] **Step 6: 提交**

```bash
git add oj.py tests/test_cli.py
git commit -m "feat: CLI 组装(fetch/list/new/test/show)"
```

---

### Task 9: 真实抓取验证 + README + 收尾

**Files:**
- Create: `README.md`
- 产生:`problems/tencent/`、`problems/bytedance/`、`problems/xiaohongshu/`(实抓)

- [ ] **Step 1: 真实抓取(用 Edge 登录态)**

Run(会触发一次 macOS 钥匙串授权):
```bash
cd ~/leetcode-oj/.claude/worktrees/leetcode-oj-build
python oj.py fetch tencent --delay 1.5
python oj.py fetch xiaohongshu --delay 1.5
python oj.py fetch bytedance --delay 1.5
```
Expected: 每个计划打印抓取进度,`problems/<公司>/` 下生成题目目录。若报"题目列表为空",说明 cookie 没拿到会员态,排查 cookies。

- [ ] **Step 2: 抽查验证**

Run:
```bash
python oj.py list tencent
python oj.py show tencent <某题slug>
```
确认题干中文正常、题目数与计划一致。

- [ ] **Step 3: 写 README.md**

内容覆盖:项目简介;前置(Python3、Edge 登录 leetcode.cn 会员);安装 `pip install -r requirements.txt`;抓取 `python oj.py fetch tencent|bytedance|xiaohongshu|all`;做题流程 `list`→`new`→编辑 `solutions/...`→`test`→`show`;**诚实说明**:本地判题仅用题目样例用例,`expected` 由题干自动抽取、可能需手工校正,拿不到官方隐藏用例;cookie 从 Edge 自动读取(钥匙串授权),失败时用 `.env` 兜底;换电脑复现 4 步(clone→install→直接做题,题库已在仓库);目录结构说明。

- [ ] **Step 4: 全量单测最终确认**

Run: `python -m pytest -v`
Expected: 全部 PASS

- [ ] **Step 5: 提交题库 + README**

```bash
git add problems solutions README.md
git commit -m "docs: README + 抓取腾讯/字节/小红书秋招真题题库"
```

- [ ] **Step 6: 合并回 main 并推送(经用户确认)**

```bash
# 退出 worktree 合并,或在 worktree 内:
git push -u origin HEAD   # 推分支;或按用户意愿合并到 main 再 push
```

---

## Self-Review

**Spec coverage:**
- 抓取三计划 → Task 6/7/9 ✓;cookie 从 Edge 读 → Task 5 ✓;离线判题 → Task 3 ✓;
  题库+题解同仓 → Task 4/9 ✓;CLI 五命令 → Task 8 ✓;HTML→MD + 模板 → Task 2 ✓;
  换电脑复现 README → Task 9 ✓;依赖限定 → Global Constraints + Task 1 ✓;
  诚实边界(样例判题/expected 抽取)→ Task 7/9 ✓。
- 新增且 spec 未明说的点:`expected` 从 `exampleTestcases` 拿不到 → 本计划明确用
  `extract_expected` 从题干抽 + 允许留空手补(Task 7),这是对 spec "样例对拍" 的必要补全。

**Placeholder scan:** 无 TBD/TODO 代码占位;runner 的 `normalize` 为预留直通函数(已说明),非占位。

**Type consistency:** `problem` dict 字段(frontend_id/title/title_slug/difficulty/url/meta/code_snippet/content_md/testcases{raw,expected})在 render/store/runner/fetch/client 间一致;`run_solution` 读 `problem["meta"]` 与 `problem["testcases"]`,与 store.load_problem 产出一致;`question_detail` 产出字段喂给 `build_problem` 一致。
