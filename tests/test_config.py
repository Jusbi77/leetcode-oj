from oj import config


def test_company_slug_known():
    assert config.company_slug("tencent") == "tencent-2023-fall-sprint"
    assert config.company_slug("bytedance") == "bytedance-2023-fall-sprint"
    assert config.company_slug("xiaohongshu") == "xiaohongshu-2023-fall-sprint"


def test_pad_id():
    assert config.pad_id(1) == "0001"
    assert config.pad_id("42") == "0042"
    assert config.pad_id(12345) == "12345"


def test_graphql_url():
    assert config.GRAPHQL_URL == "https://leetcode.cn/graphql/"


def test_dirs_under_repo_root():
    assert config.PROBLEMS_DIR == config.REPO_ROOT / "problems"
    assert config.SOLUTIONS_DIR == config.REPO_ROOT / "solutions"
