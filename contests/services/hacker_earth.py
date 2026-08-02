"""HackerEarth scraper (public events endpoint)."""
from datetime import datetime

from ..utils import UTC
from .base import BaseService


class HackerEarthService(BaseService):
    CONTESTS_URL = "https://www.hackerearth.com/chrome-extension/events"
    DATA_TYPE = "json"

    @property
    def site(self):
        return "hacker_earth"

    def extract_contests(self, data):
        return data.get("response", [])

    def extract_contest_info(self, contest):
        start = self._parse(contest["start_utc_tz"])
        end = self._parse(contest["end_utc_tz"])
        if end < self._current_time:
            return None

        return self.build_info(
            name=contest["title"],
            url=contest["url"],
            start_time=start,
            end_time=end,
            duration=(end - start).total_seconds(),
            type=contest.get("challenge_type", ""),
        )

    @staticmethod
    def _parse(value):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed
