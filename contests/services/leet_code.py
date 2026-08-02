"""LeetCode scraper (GraphQL endpoint)."""

from datetime import datetime, timedelta

from ..utils import UTC
from .base import BaseService


class LeetCodeService(BaseService):
    CONTESTS_URL = (
        "https://leetcode.com/graphql?query=%7B%20allContests%20%7B%20title%20"
        "titleSlug%20startTime%20duration%20__typename%20%7D%20%7D"
    )
    DATA_TYPE = "json"

    @property
    def site(self):
        return "leet_code"

    def extract_contests(self, data):
        return data.get("data", {}).get("allContests", [])

    def extract_contest_info(self, contest):
        start = datetime.fromtimestamp(contest["startTime"], tz=UTC)
        duration = contest.get("duration", 0)
        end = start + timedelta(seconds=duration)
        if end < self._current_time:
            return None

        return self.build_info(
            name=contest["title"],
            url=f"https://leetcode.com/contest/{contest['titleSlug']}",
            start_time=start,
            end_time=end,
            duration=duration,
        )
