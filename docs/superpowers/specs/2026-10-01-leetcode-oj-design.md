# LeetCode 企业真题本地刷题系统 — 设计文档

日期:2026-10-01
状态:待实现

## 1. 目标

一个本地命令行工具 + 本地题库仓库,围绕 leetcode.cn(中国站)的"秋招"学习计划
企业真题做题:

- **抓取一次性**:用会员登录态把指定秋招计划的题目(题干、函数签名、样例用例)
  抓到本地,固化成文件并提交进 git。
- **做题完全离线**:写 Python 题解,本地编译运行 + 样例对拍,判 AC/WA,不依赖网络。
- **换电脑即用**:`git clone` 后题库和题解都在,直接做题;只有抓新计划时才需登录态。

首批目标三个秋招学习计划:

| 公司 | 计划名 | planSlug | 题量 |
|---|---|---|---|
| 腾讯 | 腾讯秋招高效备战 | `tencent-2023-fall-sprint` | ~20 |
| 字节 | 字节跳动秋招心动计划 | `bytedance-2023-fall-sprint` | ~20 |
| 小红书 | 小红书秋招特训计划 | `xiaohongshu-2023-fall-sprint` | ~20 |

## 2. 关键事实与约束(实测确认)

- 数据源:leetcode.cn GraphQL endpoint `https://leetcode.cn/graphql/`。
- 这三个计划都是 **`premiumOnly: true`**。**匿名态下 `studyPlanV2Detail` 只返回封面信息,
  `planSubGroups` 为空数组** —— 连题目清单都拿不到。因此 **fetch 必须带会员 cookie**,
  这是硬性前提,不是可选项。
- 做题语言:**Python 3**(本地已有 python3.12)。
- cookie 来源:**从本地 Edge 浏览器的 cookie 库自动读取**(用户已在 Edge 登录 leetcode.cn)。
  Edge cookie 在 macOS 上加密存储,解密需读取钥匙串里的密钥,会触发一次钥匙串授权弹窗。
- 隐藏测试用例:LeetCode 官方不开放下载完整隐藏用例。本地判题只覆盖题目描述里的
  Example 样例用例(`exampleTestcases`),这点在 README 中明确说明。

## 3. 目录结构

```
leetcode-oj/
├── oj.py                      # CLI 入口:fetch / list / new / test / show
├── oj/
│   ├── __init__.py
│   ├── config.py              # 常量:计划映射、endpoint、路径
│   ├── cookies.py             # 从 Edge 读取 leetcode.cn 登录 cookie(含钥匙串解密)
│   ├── client.py              # leetcode.cn GraphQL 客户端(带/不带 cookie)
│   ├── fetch.py               # 抓取编排:计划 -> 题目列表 -> 单题详情 -> 落盘
│   ├── store.py               # 题库/题解的读写、路径解析、完成状态
│   ├── render.py              # 题干 HTML -> Markdown,生成 Python 模板
│   └── runner.py              # 本地判题:执行题解 + 样例对拍
├── problems/                  # 【固化题库,进 git】
│   └── tencent/
│       └── 0001.two-sum/
│           ├── problem.json       # 元数据:题干、难度、函数签名、metaData、langSlug
│           ├── testcases.json     # 样例用例(输入列表 + 期望输出)
│           └── README.md          # 渲染好的中文题干
├── solutions/                 # 【你的题解,进 git】
│   └── tencent/
│       └── 0001.two-sum.py
├── .env.example               # cookie 覆盖项示例(可选,默认从 Edge 读)
├── .gitignore
├── requirements.txt
└── README.md
```

公司短名 -> planSlug 的映射内置在 `config.py`,CLI 用 `tencent`/`bytedance`/`xiaohongshu` 短名。

## 4. 组件设计

### 4.1 cookies.py — 从 Edge 读取 cookie
- 定位 Edge cookie 文件:`~/Library/Application Support/Microsoft Edge/Default/Cookies`(SQLite)。
- Edge/Chromium 在 macOS 用 AES 加密 cookie 值,密钥存在钥匙串条目 "Microsoft Edge Safe Storage"。
  用 `security find-generic-password` 取出 → PBKDF2 派生 → AES-128-CBC 解密 cookie 值。
- 提取 `leetcode.cn` 域下的 `LEETCODE_SESSION` 和 `csrftoken`。
- 兜底:若读取失败(钥匙串拒绝、Edge 版本差异、文件锁),回退到读 `.env` 里手填的两个值,
  并打印清晰指引。
- 依赖:`pycryptodome`(AES 解密)。标准库 `sqlite3` 读 cookie 库。

### 4.2 client.py — GraphQL 客户端
- `post(query, variables, operation_name)`,统一加 header:`Content-Type`、`Origin`、
  `Referer`、`x-csrftoken`、`Cookie`。
- 两个主要查询封装:
  - `study_plan_detail(plan_slug)` → `studyPlanV2Detail`,取 `planSubGroups[].questions[]`。
  - `question_detail(title_slug)` → `question`,取 `translatedContent` / `codeSnippets` /
    `sampleTestCase` / `exampleTestcases` / `metaData` / `difficulty` / `questionFrontendId`。
- 简单限速(每题间隔 sleep),避免触发风控。
- 依赖:`requests`。

### 4.3 fetch.py — 抓取编排
1. 短名 → planSlug;读 cookie;调 `study_plan_detail` 拿题目列表(premium,必须有 cookie)。
2. 对每题调 `question_detail`,抽取:
   - 中文题干 `translatedContent`;
   - python3 模板:`codeSnippets` 中 `langSlug == "python3"` 的 `code`;
   - 样例:优先 `exampleTestcases`(多样例,`\n` 分隔),配合 `metaData.params` 解析成结构化输入;
   - `metaData`(`json.loads`):函数名 `name`、参数 `params[]{name,type}`、返回 `return.type`。
3. 落盘:`problems/<公司>/<编号.titleSlug>/` 下写 `problem.json` + `testcases.json` + `README.md`。
   编号用 `questionFrontendId` 补零 4 位。
4. 幂等:重复 fetch 覆盖题库文件,但**不覆盖 `solutions/` 下已存在的题解**。

### 4.4 render.py
- HTML 题干 → Markdown(轻量转换:标题/代码块/列表/上下标;可用 `html2text` 或自写精简版)。
- 由 `metaData` + python3 模板生成 `solutions/.../xxxx.py` 初始文件(含 `Solution` 类与签名,
  顶部注释带题号、标题、难度、链接)。

### 4.5 runner.py — 本地判题
- 从 `problem.json` 读 `metaData`(函数名、参数类型、返回类型)和 `testcases.json`。
- 动态 import 题解模块,实例化 `Solution`,反射取目标方法。
- 对每个用例:把 LeetCode 文本输入(每行一个参数的 JSON)按 `params` 顺序 `json.loads` 成实参,
  调用方法,拿返回值。
- 比对:默认 JSON 深比较;对"顺序无关"类题目(需要时按题配置)做集合/排序比较 —— 首版先做
  严格比较 + 常见归一化(如浮点容差),复杂判定留 TODO。
- 输出:逐用例 PASS/FAIL(期望 vs 实际),整体 AC/WA。

### 4.6 store.py
- 路径解析:公司短名 + 题目 slug/编号 → problems 与 solutions 路径。
- `list`:遍历某公司题库,显示编号/标题/难度 + 是否已有题解(完成状态)。

## 5. CLI 命令

| 命令 | 作用 |
|---|---|
| `python oj.py fetch tencent` | 抓腾讯计划全部题目到 `problems/tencent/`(需 cookie)。支持 `bytedance`/`xiaohongshu`,或 `all`。 |
| `python oj.py list tencent` | 列出该公司题目 + 完成状态。 |
| `python oj.py new tencent two-sum` | 在 `solutions/` 生成带签名的 Python 模板(若不存在)。 |
| `python oj.py test tencent two-sum` | 本地执行题解 + 样例对拍,输出 AC/WA。 |
| `python oj.py show tencent two-sum` | 终端查看题干。 |

题目可用 titleSlug 或题号指定。

## 6. 依赖

`requirements.txt`:
- `requests` — HTTP/GraphQL
- `pycryptodome` — 解密 Edge cookie
- `html2text` — 题干 HTML→Markdown(或自写精简版去掉此依赖)

无浏览器、无数据库。Python 标准库负责 sqlite3、json、importlib、argparse。

## 7. 换电脑复现流程(写进 README)

1. `git clone https://github.com/Jusbi77/leetcode-oj.git`
2. `pip install -r requirements.txt`
3. 直接做题:`python oj.py list tencent` → `new` → 编辑 → `test`(题库已在仓库里,全程离线)。
4. 仅当要抓新计划/更新:在该机 Edge 登录 leetcode.cn,运行 `fetch`(自动读 cookie)。

## 8. 安全与边界

- cookie 绝不写进题库、不提交 git;`.env` 在 `.gitignore` 中。从 Edge 读到的 cookie 只在
  进程内存使用。
- 抓取加间隔限速,仅抓用户会员可见的三个指定计划,不做大规模爬取。
- 本地判题覆盖样例用例,不等于官方 AC(隐藏用例拿不到)——README 明确标注。
- "提交到官方评测拿最终 AC"不在本版范围(可作为后续可选命令)。

## 9. 不做(YAGNI)

- 不做代理提交到 LeetCode 官方判题(本版聚焦本地做题)。
- 不做除 Python 外的语言。
- 不做公司 company-favorite 大题单(1000+ 题),只做指定秋招学习计划。
- 不做 Web UI。
