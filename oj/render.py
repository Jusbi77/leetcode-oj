"""题干 HTML → Markdown 的轻量转换,以及 Python 题解模板生成。"""
import re
import html as _html

_TAG = re.compile(r"<[^>]+>")


def html_to_markdown(html: str) -> str:
    """把 LeetCode 题干 HTML 转成可读的纯文本/Markdown。

    只处理常见标签(段落、换行、列表、加粗、代码块、上下标),
    其余标签直接剥离,最后统一还原 HTML 实体。
    """
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
    """由 problem dict 生成 Python 题解文件文本。

    优先使用 LeetCode 的 python3 代码模板;若缺失则按 metaData 造骨架。
    """
    header = (
        f'# {problem.get("frontend_id", "")}. {problem.get("title", "")}'
        f'  [{problem.get("difficulty", "")}]\n'
        f'# {problem.get("url", "")}\n'
        f'# title_slug: {problem.get("title_slug", "")}\n\n'
    )
    snippet = problem.get("code_snippet")
    if snippet:
        return header + snippet.rstrip() + "\n"
    meta = problem.get("meta") or {}
    name = meta.get("name", "solve")
    params = ", ".join(p["name"] for p in meta.get("params", []))
    sig = f"self, {params}" if params else "self"
    return header + f"class Solution:\n    def {name}({sig}):\n        pass\n"
