"""AtCoder scraper (parses the public contests listing page)."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from .base import BaseService

JST = ZoneInfo("Asia/Tokyo")


def parse_atcoder_time(value):
    """Parse an AtCoder timestamp, which is in Japan Standard Time (+09:00)."""
    value = value.strip()
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is not None:
        return parsed
    return parsed.replace(tzinfo=JST)


class AtCoderService(BaseService):
    CONTESTS_URL = "https://atcoder.jp/contests"
    DATA_TYPE = "html"

    @property
    def site(self):
        return "at_coder"

    def extract_contests(self, data):
        rows = []
        for table in data.select(".table-default"):
            rows.extend(table.select("tbody > tr"))
        return rows

    def extract_contest_info(self, contest):
        tds = contest.select("td")
        if len(tds) < 3:
            return None

        link = tds[1].select_one("a")
        if link is None:
            return None

        start_time = parse_atcoder_time(self._time_text(tds[0]))
        if start_time is None:
            return None

        duration = self._parse_duration(tds[2].get_text(strip=True))
        hours, minutes = duration
        seconds = hours * 3600 + minutes * 60

        return self.build_info(
            name=link.get_text(strip=True),
            url="https://atcoder.jp" + link["href"],
            start_time=start_time,
            end_time=start_time + timedelta(seconds=seconds),
            duration=seconds,
            rated_range=tds[3].get_text(strip=True) if len(tds) > 3 else "",
        )

    @staticmethod
    def _time_text(td):
        time_tag = td.select_one("time")
        if time_tag and time_tag.has_attr("datetime"):
            return time_tag["datetime"]
        if time_tag:
            return time_tag.get_text(strip=True)
        return td.get_text(strip=True)

    @staticmethod
    def _parse_duration(value):
        parts = [int(part) for part in value.split(":")]
        hours = parts[0] if parts else 0
        minutes = parts[1] if len(parts) > 1 else 0
        return hours, minutes
