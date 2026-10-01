"""项目级常量:计划映射、GraphQL endpoint、仓库路径、工具函数。"""
from pathlib import Path

GRAPHQL_URL = "https://leetcode.cn/graphql/"

REPO_ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = REPO_ROOT / "problems"
SOLUTIONS_DIR = REPO_ROOT / "solutions"

# 公司短名 -> leetcode.cn 秋招学习计划
PLANS = {
    "tencent": {"slug": "tencent-2023-fall-sprint", "name": "腾讯秋招高效备战"},
    "bytedance": {"slug": "bytedance-2023-fall-sprint", "name": "字节跳动秋招心动计划"},
    "xiaohongshu": {"slug": "xiaohongshu-2023-fall-sprint", "name": "小红书秋招特训计划"},
}


def company_slug(short: str) -> str:
    """公司短名 -> planSlug;未知短名抛 KeyError。"""
    return PLANS[short]["slug"]


def pad_id(frontend_id) -> str:
    """题号补零到 4 位,如 1 -> '0001';超过 4 位原样返回。"""
    return str(frontend_id).zfill(4)
