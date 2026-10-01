from oj import client


def test_study_plan_detail_flatten(monkeypatch):
    fake = {"studyPlanV2Detail": {"planSubGroups": [
        {"questions": [
            {"titleSlug": "two-sum", "questionFrontendId": "1", "title": "Two Sum",
             "translatedTitle": "两数之和", "difficulty": "EASY", "paidOnly": False}]},
        {"questions": [
            {"titleSlug": "add-two-numbers", "questionFrontendId": "2", "title": "Add",
             "translatedTitle": "两数相加", "difficulty": "MEDIUM", "paidOnly": True}]},
    ]}}
    c = client.LeetCodeClient(None)
    monkeypatch.setattr(c, "post", lambda *a, **k: fake)
    qs = c.study_plan_detail("tencent-2023-fall-sprint")
    assert [q["title_slug"] for q in qs] == ["two-sum", "add-two-numbers"]
    assert qs[0]["frontend_id"] == "1"


def test_question_detail_parse(monkeypatch):
    fake = {"question": {
        "questionFrontendId": "1", "title": "Two Sum", "titleSlug": "two-sum",
        "translatedTitle": "两数之和", "difficulty": "Easy", "isPaidOnly": False,
        "translatedContent": "<p>给定…</p>",
        "codeSnippets": [{"langSlug": "python", "code": "old"},
                         {"langSlug": "python3",
                          "code": "class Solution:\n    def twoSum(self): pass"}],
        "sampleTestCase": "[2,7,11,15]\n9",
        "exampleTestcases": "[2,7,11,15]\n9\n[3,2,4]\n6",
        "metaData": '{"name":"twoSum","params":[{"name":"nums","type":"integer[]"}],'
                    '"return":{"type":"integer[]"}}',
    }}
    c = client.LeetCodeClient(None)
    monkeypatch.setattr(c, "post", lambda *a, **k: fake)
    d = c.question_detail("two-sum")
    assert d["code_snippet"].startswith("class Solution")  # 选中 python3 而非 python
    assert d["meta"]["name"] == "twoSum"
    assert d["example_testcases"].count("\n") == 3
    assert d["url"] == "https://leetcode.cn/problems/two-sum/"
