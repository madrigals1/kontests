"""CodeChef scraper (public list contests API)."""

from datetime import datetime, timedelta

from ..utils import UTC
from .base import BaseService


class CodeChefService(BaseService):
    CONTESTS_URL = (
        "https://www.codechef.com/api/list/contests/all"
        "?sort_by=START&sorting_order=asc&offset=0&mode=all"
    )
    DATA_TYPE = "json"

    @property
    def site(self):
        return "code_chef"

    def extract_contests(self, data):
        contests = data.get("present_contests", []) + data.get("future_contests", [])
        return list(reversed(contests))

    def extract_contest_info(self, contest):
        start = self._parse(contest["contest_start_date_iso"])
        end = None
        duration = contest.get("contest_duration")

        if contest.get("contest_end_date_iso"):
            end = self._parse(contest["contest_end_date_iso"])
            if duration is not None:
                duration = int(duration) * 60
        else:
            end = start + timedelta(days=3650)  # 10 years
            duration = (end - start).total_seconds()

        return self.build_info(
            name=contest["contest_name"],
            url=f"https://www.codechef.com/{contest['contest_code']}",
            start_time=start,
            end_time=end,
            duration=duration,
        )

    @staticmethod
    def _parse(value):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed
