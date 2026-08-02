"""Toph scraper (parses the contests listing page)."""

from datetime import datetime

from ..utils import UTC
from .base import BaseService

CONTAINER_INDEX = 1


class TophService(BaseService):
    CONTESTS_URL = "https://toph.co/contests"
    DATA_TYPE = "html"

    @property
    def site(self):
        return "toph"

    def extract_contests(self, data):
        containers = data.select(".container")
        if len(containers) <= CONTAINER_INDEX:
            return []
        row = containers[CONTAINER_INDEX].select_one(".row")
        if row is None:
            return []
        col = row.select_one(".col-md-9")
        return col.select(".panel") if col else []

    def extract_contest_info(self, contest):
        try:
            caption = contest.select_one(".caption")
            timestamp = contest.select_one(".timestamp")

            name = caption.select_one("h2").get_text(strip=True) if caption else ""
            href = caption["href"] if caption and caption.has_attr("href") else ""
            url = "https://toph.co" + href

            start = None
            if timestamp and timestamp.has_attr("data-time"):
                start = datetime.fromtimestamp(int(timestamp["data-time"]), tz=UTC)
            if start is None:
                return None

            text = contest.get_text()

            return self.build_info(
                name=name,
                url=url,
                start_time=start,
                end_time=start,
                duration=0,
                is_rated="Yes" if "Rated" in text else "No",
                is_official="Yes" if "Official" in text else "No",
            )
        except Exception:
            return None
