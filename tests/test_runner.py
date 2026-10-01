import textwrap

from oj import runner


def test_parse_inputs_two_params():
    raw = "[2,7,11,15]\n9\n[3,2,4]\n6"
    params = [{"name": "nums", "type": "integer[]"}, {"name": "target", "type": "integer"}]
    groups = runner.parse_inputs(raw, params)
    assert groups == [[[2, 7, 11, 15], 9], [[3, 2, 4], 6]]


def test_compare_float_tolerance():
    assert runner.compare(1.0, 1.0 + 1e-7) is True
    assert runner.compare([1, 2], [1, 2]) is True
    assert runner.compare([1, 2], [2, 1]) is False


def test_run_solution_ac(tmp_path):
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
        "meta": {"name": "twoSum", "params": [
            {"name": "nums", "type": "integer[]"}, {"name": "target", "type": "integer"}]},
        "testcases": {"raw": "[2,7,11,15]\n9\n[3,2,4]\n6", "expected": [[0, 1], [1, 2]]},
    }
    result = runner.run_solution(str(sol), problem)
    assert result["ac"] is True
    assert result["passed"] == 2 and result["total"] == 2


def test_run_solution_wa(tmp_path):
    sol = tmp_path / "sol.py"
    sol.write_text("class Solution:\n    def twoSum(self, nums, target):\n        return [9,9]\n")
    problem = {
        "meta": {"name": "twoSum", "params": [
            {"name": "nums", "type": "integer[]"}, {"name": "target", "type": "integer"}]},
        "testcases": {"raw": "[2,7,11,15]\n9", "expected": [[0, 1]]},
    }
    result = runner.run_solution(str(sol), problem)
    assert result["ac"] is False
    assert result["cases"][0]["ok"] is False
