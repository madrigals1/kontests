"""TopCoder scraper, backed by its public Google Calendar feed."""
from datetime import datetime

from ..utils import UTC
from .base import BaseService


class TopCoderService(BaseService):
    CONTESTS_URL = (
        "https://clients6.google.com/calendar/v3/calendars/"
        "appirio.com_bhga3musitat85mhdrng9035jg@group.calendar.google.com/events"
        "?calendarId=appirio.com_bhga3musitat85mhdrng9035jg%40group.calendar.google.com"
        "&timeMin=2019-01-01T00%3A00%3A00-04%3A00"
        "&key=AIzaSyBNlYH01_9Hc5S1J9vuFmu2nUqBZJNAXxs"
    )
    DATA_TYPE = "json"

    @property
    def site(self):
        return "top_coder"

    def extract_contests(self, data):
        items = [
            element
            for element in data.get("items", [])
            if element.get("start", {}).get("dateTime")
        ]
        return sorted(items, key=lambda element: element["start"]["dateTime"])

    def extract_contest_info(self, contest):
        start = self._parse(contest["start"]["dateTime"])
        end = self._parse(contest["end"]["dateTime"])
        if end < self._current_time:
            return None

        return self.build_info(
            name=contest["summary"],
            url="https://www.topcoder.com/challenges",
            start_time=start,
            end_time=end,
            duration=(end - start).total_seconds(),
        )

    @staticmethod
    def _parse(value):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed
