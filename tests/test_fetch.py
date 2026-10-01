from oj import fetch


def test_extract_expected_cn():
    html = ("<p>示例 1:</p><pre>输入:nums = [2,7,11,15], target = 9\n输出:[0,1]</pre>"
            "<p>示例 2:</p><pre>输入:nums = [3,2,4], target = 6\n输出:[1,2]</pre>")
    assert fetch.extract_expected(html) == [[0, 1], [1, 2]]


def test_build_problem_shape():
    detail = {
        "frontend_id": "1", "title": "两数之和", "title_slug": "two-sum", "difficulty": "EASY",
        "url": "https://leetcode.cn/problems/two-sum/",
        "content_html": "<pre>输入:nums=[2,7], target=9\n输出:[0,1]</pre>",
        "code_snippet": "class Solution:\n    def twoSum(self): pass",
        "meta": {"name": "twoSum", "params": [{"name": "nums", "type": "integer[]"}],
                 "return": {"type": "integer[]"}},
        "example_testcases": "[2,7]\n9", "sample_testcase": "[2,7]\n9",
    }
    p = fetch.build_problem(detail)
    assert p["testcases"]["raw"] == "[2,7]\n9"
    assert p["testcases"]["expected"] == [[0, 1]]
    assert "content_md" in p and "<pre>" not in p["content_md"]


def test_fetch_company_uses_client(tmp_path):
    class FakeClient:
        def study_plan_detail(self, slug):
            return [{"title_slug": "two-sum", "frontend_id": "1", "difficulty": "EASY"}]

        def question_detail(self, slug):
            return {"frontend_id": "1", "title": "两数之和", "title_slug": "two-sum",
                    "difficulty": "EASY", "url": "u",
                    "content_html": "<pre>输出:[0,1]</pre>",
                    "code_snippet": "class Solution:\n    pass",
                    "meta": {"name": "twoSum", "params": []},
                    "example_testcases": "[2,7]\n9", "sample_testcase": ""}

    n = fetch.fetch_company("tencent", client=FakeClient(), delay=0, root=tmp_path)
    assert n == 1
    assert (tmp_path / "problems" / "tencent" / "0001.two-sum" / "problem.json").exists()
