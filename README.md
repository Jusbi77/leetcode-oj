# leetcode-oj — LeetCode 企业真题本地刷题系统

把 leetcode.cn 上的「秋招」企业真题学习计划抓到本地,固化成文件,**离线做题 + 本地样例判题**。
题库和题解都提交进 git,换一台电脑 `clone` 下来即可直接做题。

当前内置三个秋招学习计划:

| 公司 | 计划 | 短名 | 题量 |
|---|---|---|---|
| 腾讯 | 腾讯秋招高效备战 | `tencent` | 20 |
| 小红书 | 小红书秋招特训计划 | `xiaohongshu` | 23 |
| 字节 | 字节跳动秋招心动计划 | `bytedance` | 20 |

## 快速开始

```bash
git clone https://github.com/Jusbi77/leetcode-oj.git
cd leetcode-oj
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

题库已经在仓库里,装完依赖就能直接做题,**无需再抓取、无需登录**:

```bash
python oj.py list tencent                 # 列出腾讯题目和完成状态
python oj.py show tencent valid-palindrome # 看题干
python oj.py new  tencent valid-palindrome # 生成题解模板到 solutions/
# 编辑 solutions/tencent/0125.valid-palindrome.py,写你的解法
python oj.py test tencent valid-palindrome # 本地样例判题,输出 AC/WA
```

> 做题、判题、看题全程**离线**,只用 Python 标准库,不碰网络、不碰登录态。
> `requests` / `pycryptodome` 只有「抓取新题目」时才需要。

## 命令一览

| 命令 | 作用 |
|---|---|
| `python oj.py list <公司>` | 列出该公司题目 + 完成状态(✅/⬜)和进度 |
| `python oj.py show <公司> <题>` | 终端查看中文题干 |
| `python oj.py new  <公司> <题>` | 在 `solutions/` 生成带函数签名的 Python 模板 |
| `python oj.py test <公司> <题>` | 本地运行题解 + 样例对拍,判 AC/WA |
| `python oj.py fetch <公司>` | 抓取/更新题库(需登录态,见下) |

`<公司>` = `tencent` / `xiaohongshu` / `bytedance`。
`<题>` 可用 titleSlug(如 `valid-palindrome`)或题号(如 `125`)。
`fetch` 还支持 `all` 一次抓三家。

## 抓取新题目(需要 leetcode.cn 会员登录态)

这三个计划是**会员专属**,匿名拿不到题目列表,所以 `fetch` 需要你的登录 cookie。
**抓取是一次性的**:抓完题库就固化在仓库里,之后做题和换电脑都不再需要 cookie。

cookie 获取优先级:`.env` / 环境变量 > 本地缓存 `.cookies.json` > 从 Edge 自动读取。

### 方式一:手动填 .env(推荐,最稳)

1. 在浏览器打开已登录的 `https://leetcode.cn`
2. `F12` → **Application** → 左侧 **Cookies** → `https://leetcode.cn`
3. 复制 `LEETCODE_SESSION` 和 `csrftoken` 两个值
4. 复制 `.env.example` 为 `.env`,填入:

```
LEETCODE_SESSION=你的session值
LEETCODE_CSRFTOKEN=你的csrftoken值
```

5. `python oj.py fetch tencent`

`.env` 和 `.cookies.json` 都在 `.gitignore` 里,**绝不会被提交**。

### 方式二:从 Edge 自动读取(macOS)

若不填 `.env`,工具会尝试从本地 Edge 的 cookie 库读取(需解密,触发一次 macOS 钥匙串授权)。
弹窗出现时点「始终允许」。读到后会缓存到 `.cookies.json`,后续不再弹窗。
> 注:部分机器上钥匙串对 CLI 调用会反复弹窗,此时请改用方式一。

## 本地判题的边界(重要)

- 判题使用的测试用例来自**题目描述里的示例(Example)**:输入取自 LeetCode 的 `exampleTestcases`,
  期望输出从题干「输出:」处自动抽取。本仓库 63 题中 **61 题**成功抽到期望输出可直接判题。
- **拿不到官方隐藏测试用例**——LeetCode 不开放下载。所以本地 AC 只代表「样例通过」,
  不等于官方 AC。最终以 leetcode.cn 提交为准。
- **少数设计类题**(如 146 LRU 缓存,多方法调用)没有单一函数签名,本地判题器判不了,
  其 `testcases.json` 的 `expected` 为空,`test` 会提示你在该文件手动补充。
- 浮点结果判题带 `1e-5` 容差;结果顺序敏感(如需顺序无关比较请自行调整 runner)。

## 目录结构

```
oj.py                     # CLI 入口
oj/                       # 核心包
  config.py               # 计划映射、路径、常量
  cookies.py              # 从 Edge/.env 读取 cookie(仅 fetch 用)
  client.py               # leetcode.cn GraphQL 客户端
  fetch.py                # 抓取编排
  render.py               # 题干 HTML→Markdown、题解模板
  store.py                # 题库/题解读写、路径、完成状态
  runner.py               # 本地判题
problems/<公司>/<编号.slug>/   # 固化题库(进 git)
  problem.json            # 题干元数据、函数签名、python3 模板
  testcases.json          # 样例输入 + 期望输出
  README.md               # 渲染好的中文题干
solutions/<公司>/<编号.slug>.py  # 你的题解(进 git)
tests/                    # pytest 单测
```

## 开发

```bash
pip install -r requirements.txt
python -m pytest -q          # 跑单测
```
