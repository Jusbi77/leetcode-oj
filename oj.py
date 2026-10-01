#!/usr/bin/env python3
"""LeetCode 企业真题本地刷题 CLI。

子命令:fetch / list / new / test / show
"""
import argparse
import sys

from oj import config, store, runner, fetch

_DIFF_CN = {"EASY": "简单", "MEDIUM": "中等", "HARD": "困难",
            "Easy": "简单", "Medium": "中等", "Hard": "困难"}


def _diff(d):
    return _DIFF_CN.get(d, d or "")


def cmd_fetch(args):
    targets = ["tencent", "bytedance", "xiaohongshu"] if args.company == "all" else [args.company]
    for t in targets:
        if t not in config.PLANS:
            print(f"未知公司:{t}(可选:tencent / bytedance / xiaohongshu / all)")
            return 2
        print(f"抓取 {config.PLANS[t]['name']} ({config.company_slug(t)}) …")
        n = fetch.fetch_company(t, delay=args.delay)
        print(f"✓ {t}: {n} 题\n")
    return 0


def cmd_list(args):
    items = store.list_problems(args.company)
    if not items:
        print(f"{args.company}: 暂无题目,先运行:python oj.py fetch {args.company}")
        return 0
    for it in items:
        mark = "✅" if it["solved"] else "⬜"
        print(f"{mark} {config.pad_id(it['frontend_id'])}. {it['title']}  "
              f"[{_diff(it['difficulty'])}]  ({it['title_slug']})")
    done = sum(1 for i in items if i["solved"])
    print(f"\n进度:{done}/{len(items)}")
    return 0


def cmd_new(args):
    p = store.load_problem(args.company, args.problem)
    path, created = store.ensure_solution(args.company, p)
    print(("已创建 " if created else "已存在 ") + str(path))
    return 0


def cmd_test(args):
    p = store.load_problem(args.company, args.problem)
    path, _ = store.ensure_solution(args.company, p)
    result = runner.run_solution(str(path), p)
    for i, c in enumerate(result["cases"]):
        tag = "PASS" if c["ok"] else "FAIL"
        line = (f"  用例{i + 1} {tag}  输入={c['input']}  "
                f"期望={c['expected']}  实际={c.get('got')}")
        if c.get("error"):
            line += f"  错误={c['error']}"
        print(line)
    verdict = "AC ✅" if result["ac"] else "WA ❌"
    print(f"\n{p['title']}: {verdict}  ({result['passed']}/{result['total']})")
    if result["total"] == 0 or not p["testcases"].get("expected"):
        print("  注意:该题缺少本地期望输出,请在 "
              f"problems/{args.company}/.../testcases.json 的 expected 补上。")
    return 0


def cmd_show(args):
    p = store.load_problem(args.company, args.problem)
    d = store.problem_dir(args.company, p["frontend_id"], p["title_slug"])
    print((d / "README.md").read_text())
    return 0


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(prog="oj", description="LeetCode 企业真题本地刷题")
    sub = ap.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("fetch", help="抓取公司秋招计划题目(需 Edge 登录会员)")
    f.add_argument("company", help="tencent / bytedance / xiaohongshu / all")
    f.add_argument("--delay", type=float, default=1.0, help="每题间隔秒数,默认 1.0")
    f.set_defaults(func=cmd_fetch)

    l = sub.add_parser("list", help="列出某公司题目与完成状态")
    l.add_argument("company")
    l.set_defaults(func=cmd_list)

    n = sub.add_parser("new", help="生成题解模板文件")
    n.add_argument("company")
    n.add_argument("problem", help="titleSlug 或题号")
    n.set_defaults(func=cmd_new)

    t = sub.add_parser("test", help="本地运行题解并样例对拍")
    t.add_argument("company")
    t.add_argument("problem", help="titleSlug 或题号")
    t.set_defaults(func=cmd_test)

    s = sub.add_parser("show", help="查看题干")
    s.add_argument("company")
    s.add_argument("problem", help="titleSlug 或题号")
    s.set_defaults(func=cmd_show)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
