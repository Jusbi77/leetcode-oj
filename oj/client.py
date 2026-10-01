"""leetcode.cn GraphQL 客户端:学习计划详情、单题详情。"""
import json

import requests

from oj import config

_PLAN_QUERY = """
query studyPlanV2Detail($planSlug: String!) {
  studyPlanV2Detail(planSlug: $planSlug) {
    slug name premiumOnly questionNum
    planSubGroups { name questionNum
      questions { titleSlug questionFrontendId title translatedTitle difficulty paidOnly } } } }
"""

_QUESTION_QUERY = """
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionFrontendId title titleSlug translatedTitle difficulty isPaidOnly
    translatedContent content
    codeSnippets { lang langSlug code }
    sampleTestCase exampleTestcases metaData } }
"""


class LeetCodeClient:
    def __init__(self, cookies: dict | None):
        self.s = requests.Session()
        self.cookies = cookies or {}
        self.s.headers.update({
            "Content-Type": "application/json",
            "Origin": "https://leetcode.cn",
            "Referer": "https://leetcode.cn/",
            "User-Agent": "Mozilla/5.0 leetcode-oj",
        })
        if self.cookies:
            self.s.headers["x-csrftoken"] = self.cookies.get("csrftoken", "")
            self.s.headers["Cookie"] = "; ".join(f"{k}={v}" for k, v in self.cookies.items())

    def post(self, query, variables, operation_name):
        r = self.s.post(
            config.GRAPHQL_URL,
            json={"query": query, "variables": variables, "operationName": operation_name},
            timeout=30)
        r.raise_for_status()
        body = r.json()
        if body.get("errors"):
            raise RuntimeError(f"GraphQL error: {body['errors']}")
        return body["data"]

    def study_plan_detail(self, plan_slug):
        """返回学习计划的题目列表(扁平化 planSubGroups)。"""
        data = self.post(_PLAN_QUERY, {"planSlug": plan_slug}, "studyPlanV2Detail")
        detail = data.get("studyPlanV2Detail") or {}
        out = []
        for grp in detail.get("planSubGroups") or []:
            for q in grp.get("questions") or []:
                out.append({
                    "title_slug": q["titleSlug"],
                    "frontend_id": q["questionFrontendId"],
                    "title": q.get("title"),
                    "translated_title": q.get("translatedTitle"),
                    "difficulty": q.get("difficulty"),
                    "paid_only": q.get("paidOnly"),
                })
        return out

    def question_detail(self, title_slug):
        """返回单题详情:题干、python3 模板、样例、metaData 等。"""
        data = self.post(_QUESTION_QUERY, {"titleSlug": title_slug}, "questionData")
        q = data.get("question") or {}
        snippet = ""
        for cs in q.get("codeSnippets") or []:
            if cs.get("langSlug") == "python3":
                snippet = cs["code"]
                break
        meta = json.loads(q["metaData"]) if q.get("metaData") else {}
        return {
            "frontend_id": q.get("questionFrontendId"),
            "title": q.get("translatedTitle") or q.get("title"),
            "title_slug": q.get("titleSlug") or title_slug,
            "difficulty": q.get("difficulty"),
            "url": f"https://leetcode.cn/problems/{title_slug}/",
            "content_html": q.get("translatedContent") or q.get("content") or "",
            "code_snippet": snippet,
            "meta": meta,
            "example_testcases": q.get("exampleTestcases") or "",
            "sample_testcase": q.get("sampleTestCase") or "",
        }
