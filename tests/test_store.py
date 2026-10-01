from oj import store

PROBLEM = {
    "frontend_id": "1", "title": "两数之和", "title_slug": "two-sum",
    "difficulty": "EASY", "url": "https://leetcode.cn/problems/two-sum/",
    "content_md": "给定数组…",
    "code_snippet": "class Solution:\n    def twoSum(self, nums, target):\n        pass",
    "meta": {"name": "twoSum", "params": [{"name": "nums", "type": "integer[]"}],
             "return": {"type": "integer[]"}},
    "testcases": {"raw": "[2,7,11,15]\n9", "expected": [[0, 1]]},
}


def test_save_and_load_problem(tmp_path):
    store.save_problem("tencent", PROBLEM, root=tmp_path)
    loaded = store.load_problem("tencent", "two-sum", root=tmp_path)
    assert loaded["title"] == "两数之和"
    assert loaded["testcases"]["expected"] == [[0, 1]]
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
