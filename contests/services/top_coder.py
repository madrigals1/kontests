"""TopCoder scraper, backed by its public Google Calendar feed."""
import os
from datetime import datetime
from urllib.parse import quote

from ..constants import UNKNOWN
from ..utils import UTC
from .base import BaseService

# The calendar identifier and the minimum start time (UTC) are stable, but the
# Google API key must come from the environment so it is never committed.
CALENDAR_ID = "appirio.com_bhga3musitat85mhdrng9035jg@group.calendar.google.com"
TIME_MIN = "2019-01-01T00:00:00-04:00"

API_KEY = os.environ.get("TOPCODER_CALENDAR_KEY", "")


class TopCoderService(BaseService):
    DATA_TYPE = "json"

    @property
    def CONTESTS_URL(self):
        # Built dynamically so the API key stays in the environment.
        encoded_id = quote(CALENDAR_ID, safe="")
        return (
            "https://clients6.google.com/calendar/v3/calendars/"
            f"{encoded_id}/events"
            f"?calendarId={encoded_id}"
            f"&timeMin={quote(TIME_MIN, safe='')}"
            f"&key={API_KEY}"
        )

    @property
    def site(self):
        return "top_coder"

    def fetch(self):
        if not API_KEY:
            from django.core.exceptions import ImproperlyConfigured

            raise ImproperlyConfigured(
                "Set TOPCODER_CALENDAR_KEY in the environment to scrape TopCoder."
            )
        return super().fetch()

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
