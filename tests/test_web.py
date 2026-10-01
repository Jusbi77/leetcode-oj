from oj import web, store


PROBLEM = {
    "frontend_id": "125", "title": "验证回文串", "title_slug": "valid-palindrome",
    "difficulty": "Easy", "url": "u", "content_md": "题干",
    "code_snippet": "class Solution:\n    def isPalindrome(self, s):\n        pass",
    "meta": {"name": "isPalindrome", "params": [{"name": "s", "type": "string"}]},
    "testcases": {"raw": '"aba"\n"ab"', "expected": [True, False]},
}


def test_run_code_ac(tmp_path, monkeypatch):
    from oj import config
    monkeypatch.setattr(config, "REPO_ROOT", tmp_path)
    store.save_problem("tencent", PROBLEM, root=tmp_path)
    code = ("class Solution:\n"
            "    def isPalindrome(self, s):\n"
            "        t=[c.lower() for c in s if c.isalnum()]\n"
            "        return t==t[::-1]\n")
    result = web.run_code("tencent", "valid-palindrome", code)
    assert result["ac"] is True
    assert result["passed"] == 2


def test_problem_payload_shape(tmp_path, monkeypatch):
    from oj import config
    monkeypatch.setattr(config, "REPO_ROOT", tmp_path)
    store.save_problem("tencent", PROBLEM, root=tmp_path)
    payload = web._problem_payload("tencent", "valid-palindrome")
    assert payload["title"] == "验证回文串"
    assert payload["has_expected"] is True
    assert "isPalindrome" in payload["code"]
