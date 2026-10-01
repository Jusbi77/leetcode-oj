"""项目级常量:计划映射、GraphQL endpoint、仓库路径、工具函数。"""
from pathlib import Path

GRAPHQL_URL = "https://leetcode.cn/graphql/"

REPO_ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = REPO_ROOT / "problems"
SOLUTIONS_DIR = REPO_ROOT / "solutions"

# 公司短名 -> leetcode.cn 秋招学习计划
PLANS = {
    "tencent":     {"slug": "tencent-2023-fall-sprint",     "name": "腾讯秋招高效备战"},
    "bytedance":   {"slug": "bytedance-2023-fall-sprint",   "name": "字节跳动秋招心动计划"},
    "xiaohongshu": {"slug": "xiaohongshu-2023-fall-sprint", "name": "小红书秋招特训计划"},
    "huawei":      {"slug": "huawei-2023-fall-sprint",      "name": "华为秋招冲刺计划"},
    "alibaba":     {"slug": "ali-2023-fall-sprint",          "name": "阿里秋招面试宝典"},
    "jd":          {"slug": "jd-2023-fall-sprint",          "name": "京东秋招多快好省备考计划"},
    "meituan":     {"slug": "meituan-2023-fall-sprint",     "name": "美团秋招攻略"},
    "kuaishou":    {"slug": "kuaishou-2023-fall-sprint",    "name": "快手秋招真题在手"},
    "xiaomi":      {"slug": "mi-2023-fall-sprint",          "name": "小米秋招真题笔记"},
    "didi":        {"slug": "didi-2023-fall-sprint",        "name": "滴滴秋招橙意计划"},
    "baidu":       {"slug": "baidu-2023-fall-sprint",       "name": "百度秋招突击手册"},
    "mihoyo":      {"slug": "mihoyo-2023-fall-sprint",      "name": "米哈游秋招面试题通关"},
    "pdd":         {"slug": "pdd-2023-fall-sprint",         "name": "拼多多秋招备战方略"},
    "dp":          {"slug": "dynamic-programming-grandmaster", "name": "动态规划（进阶版）"},
}


def company_slug(short: str) -> str:
    """公司短名 -> planSlug;未知短名抛 KeyError。"""
    return PLANS[short]["slug"]


def pad_id(frontend_id) -> str:
    """题号补零到 4 位,如 1 -> '0001';超过 4 位原样返回。"""
    return str(frontend_id).zfill(4)
