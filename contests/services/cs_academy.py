"""CS Academy scraper (parses the contests listing page)."""

import re
from datetime import datetime

from ..utils import UTC
from .base import BaseService


class CsAcademyService(BaseService):
    CONTESTS_URL = "https://csacademy.com/contests"
    DATA_TYPE = "html"

    @property
    def site(self):
        return "cs_academy"

    def extract_contests(self, data):
        tables = data.select("table")
        if tables:
            tables.pop()
        return tables

    def extract_contest_info(self, table):
        info = []
        for contest in table.select("tbody tr"):
            tds = contest.select("td")
            if len(tds) < 3:
                continue

            link = tds[0].select_one("a")
            start_time = self._parse_start(tds[1].get_text(" ", strip=True))
            duration = self._parse_duration(tds[2].get_text(" ", strip=True))

            info.append(
                self.build_info(
                    name=link.get_text(strip=True) if link else "",
                    url="https://csacademy.com" + link["href"] if link else "",
                    start_time=start_time,
                    end_time=start_time + duration,
                    duration=duration.total_seconds(),
                )
            )
        return info

    @staticmethod
    def _parse_start(value):
        match = re.search(r"(\d{1,2}\s+\w+\s+\d{4})\s+(\d{1,2}:\d{2})", value)
        if not match:
            return None
        parsed = datetime.strptime(
            f"{match.group(1)} {match.group(2)}", "%d %B %Y %H:%M"
        )
        return parsed.replace(tzinfo=UTC)

    @staticmethod
    def _parse_duration(value):
        from datetime import timedelta

        numbers = [int(token) for token in value.split() if token.isdigit()]
        hours = numbers[0] if numbers else 0
        minutes = numbers[1] if len(numbers) > 1 else 0
        return timedelta(hours=hours, minutes=minutes)
