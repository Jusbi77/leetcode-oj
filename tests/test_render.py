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
        "meta": {"name": "twoSum", "params": [{"name": "nums", "type": "integer[]"}],
                 "return": {"type": "integer[]"}},
    }
    text = render.build_solution_template(problem)
    assert "class Solution:" in text
    assert "def twoSum" in text
    assert "两数之和" in text and "two-sum" in text
