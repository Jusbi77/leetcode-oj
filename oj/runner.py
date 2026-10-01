"""本地判题:动态加载题解,用样例用例对拍。纯标准库,无网络。"""
import json
import math
import importlib.util


def parse_inputs(raw: str, params: list) -> list:
    """把 exampleTestcases 文本切成多组实参。

    每 len(params) 行为一组,每行是一个 JSON 值,按 params 顺序解析。
    """
    n = len(params) or 1
    lines = [ln for ln in (raw or "").splitlines() if ln.strip() != ""]
    groups = []
    for i in range(0, len(lines), n):
        chunk = lines[i:i + n]
        if len(chunk) < n:
            break
        groups.append([json.loads(x) for x in chunk])
    return groups


def compare(expected, actual) -> bool:
    """深比较;浮点带 1e-5 容差;list/dict 递归比较。"""
    if isinstance(expected, bool) or isinstance(actual, bool):
        return expected == actual
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
    """预留:复杂题型(顺序无关等)的归一化;首版直通。"""
    return value


def _load_solution(path: str):
    spec = importlib.util.spec_from_file_location("_oj_sol", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.Solution()


def run_solution(solution_path: str, problem: dict) -> dict:
    """执行题解并逐用例对拍。

    返回 {"passed", "total", "ac", "cases": [{"ok","input","expected","got"[,"error"]}]}。
    """
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
    except Exception as e:  # 加载/找方法失败:全部用例判错
        for i, args in enumerate(groups):
            cases.append({"ok": False, "input": args,
                          "expected": expected[i] if i < len(expected) else None,
                          "got": None, "error": f"load error: {e}"})
        return {"passed": 0, "total": len(groups), "ac": len(groups) == 0, "cases": cases}

    passed = 0
    for i, args in enumerate(groups):
        exp = expected[i] if i < len(expected) else None
        try:
            # 深拷贝实参,避免题解就地修改影响后续用例
            call_args = [json.loads(json.dumps(a)) for a in args]
            got = method(*call_args)
            ok = compare(exp, got) if i < len(expected) else False
        except Exception as e:
            cases.append({"ok": False, "input": args, "expected": exp, "got": None, "error": str(e)})
            continue
        if ok:
            passed += 1
        cases.append({"ok": ok, "input": args, "expected": exp, "got": got})

    total = len(groups)
    # 没有期望输出时无法判 AC
    has_expected = len(expected) > 0
    return {"passed": passed, "total": total,
            "ac": has_expected and total > 0 and passed == total, "cases": cases}
