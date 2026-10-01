"""抓取编排:学习计划 -> 题目列表 -> 单题详情 -> 落盘。"""
import re
import json
import time
import html as _html

from oj import config, cookies as cookies_mod, client as client_mod, store, render

_OUT_RE = re.compile(r"(?:输出|Output)\s*[:：]\s*(.+)")


def extract_expected(content_html: str) -> list:
    """从题干 Example 块里抽取每个"输出:"后的期望值。

    LeetCode 的 exampleTestcases 只有输入没有期望输出,这里从题干正文补齐。
    抽不出合法 JSON 时退化为去引号的字符串。
    """
    text = _html.unescape(re.sub(r"<[^>]+>", "\n", content_html or ""))
    out = []
    for m in _OUT_RE.finditer(text):
        raw = m.group(1).strip()
        raw = raw.split("\n")[0].strip().rstrip("。.")
        try:
            out.append(json.loads(raw))
        except Exception:
            out.append(raw.strip('"'))
    return out


def build_problem(detail: dict) -> dict:
    """把 client.question_detail 的结果转成 store.save_problem 所需结构。"""
    expected = extract_expected(detail.get("content_html", ""))
    return {
        "frontend_id": detail["frontend_id"],
        "title": detail["title"],
        "title_slug": detail["title_slug"],
        "difficulty": detail["difficulty"],
        "url": detail["url"],
        "meta": detail.get("meta", {}),
        "code_snippet": detail.get("code_snippet", ""),
        "content_md": render.html_to_markdown(detail.get("content_html", "")),
        "testcases": {"raw": detail.get("example_testcases", ""), "expected": expected},
    }


def fetch_company(short: str, client=None, delay: float = 1.0, root=None) -> int:
    """抓取一个公司的秋招计划全部题目并落盘,返回题目数。"""
    if client is None:
        c = cookies_mod.get_leetcode_cookies()
        client = client_mod.LeetCodeClient(c)
    plan_slug = config.company_slug(short)
    questions = client.study_plan_detail(plan_slug)
    if not questions:
        raise RuntimeError(
            f"{short}: 题目列表为空。该计划为会员专属,"
            "请确认 Edge 已登录 leetcode.cn 会员账号。")
    count = 0
    total = len(questions)
    for q in questions:
        detail = client.question_detail(q["title_slug"])
        problem = build_problem(detail)
        store.save_problem(short, problem, root=root)
        count += 1
        print(f"  [{count}/{total}] {problem['frontend_id']}. {problem['title']}")
        if delay:
            time.sleep(delay)
    return count
