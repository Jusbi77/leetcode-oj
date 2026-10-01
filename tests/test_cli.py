import importlib.util
from pathlib import Path


def _load_cli():
    spec = importlib.util.spec_from_file_location(
        "ojcli", Path(__file__).resolve().parent.parent / "oj.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_list_new_test_commands(tmp_path, monkeypatch, capsys):
    from oj import store, config
    monkeypatch.setattr(config, "REPO_ROOT", tmp_path)

    problem = {
        "frontend_id": "1", "title": "两数之和", "title_slug": "two-sum", "difficulty": "EASY",
        "url": "u", "content_md": "题",
        "code_snippet": ("class Solution:\n"
                         "    def twoSum(self, nums, target):\n"
                         "        seen = {}\n"
                         "        for i, n in enumerate(nums):\n"
                         "            if target - n in seen:\n"
                         "                return [seen[target - n], i]\n"
                         "            seen[n] = i"),
        "meta": {"name": "twoSum", "params": [
            {"name": "nums", "type": "integer[]"}, {"name": "target", "type": "integer"}]},
        "testcases": {"raw": "[2,7,11,15]\n9", "expected": [[0, 1]]},
    }
    store.save_problem("tencent", problem, root=tmp_path)

    cli = _load_cli()
    assert cli.main(["list", "tencent"]) == 0
    assert cli.main(["new", "tencent", "two-sum"]) == 0

    # 用正确题解覆盖模板,test 应判 AC
    sp = tmp_path / "solutions" / "tencent" / "0001.two-sum.py"
    sp.write_text(problem["code_snippet"])
    assert cli.main(["test", "tencent", "two-sum"]) == 0
    out = capsys.readouterr().out
    assert "AC" in out
