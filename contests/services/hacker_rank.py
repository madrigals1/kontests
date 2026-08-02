"""HackerRank scraper (public REST endpoints)."""
from datetime import datetime

import requests

from .base import USER_AGENT, BaseService
from ..utils import UTC

UPCOMING_URL = "https://www.hackerrank.com/rest/contests/upcoming?limit=100"
COLLEGE_URL = "https://www.hackerrank.com/rest/contests/college?limit=100"


class HackerRankService(BaseService):
    @property
    def site(self):
        return "hacker_rank"

    def fetch(self):
        response1 = self._request(UPCOMING_URL)
        response2 = self._request(COLLEGE_URL)
        return (self.parse_json(response1), self.parse_json(response2))

    def _request(self, url):
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=self.TIMEOUT,
        )
        response.raise_for_status()
        return response.text

    def extract_contests(self, data):
        data1, data2 = data
        regular = [dict(element, type_="Regular") for element in data1.get("models", [])]
        college = [dict(element, type_="College") for element in data2.get("models", [])]
        return sorted(
            regular + college, key=lambda element: element.get("epoch_starttime", 0)
        )

    def extract_contest_info(self, contest):
        start = self._epoch(contest.get("epoch_starttime"))
        end = self._epoch(contest.get("epoch_endtime"))
        if end is None or end < self._current_time:
            return None

        return self.build_info(
            name=contest["name"],
            url=f"https://hackerrank.com/contests/{contest['slug']}",
            start_time=start,
            end_time=end,
            duration=(end - start).total_seconds() if start else None,
            type=contest.get("type_", ""),
        )

    @staticmethod
    def _epoch(value):
        if value is None:
            return None
        return datetime.fromtimestamp(int(value), tz=UTC)
