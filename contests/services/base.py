"""Base class shared by every site scraper."""

import json
import logging
from datetime import timedelta

import requests
from bs4 import BeautifulSoup
from django.db import transaction
from django.utils import timezone

from ..models import Contest, LastUpdate
from ..utils import UTC, guess_status, in_24_hours

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0"
)


class BaseService:
    """Fetch, parse and store contests for a single site.

    Subclasses only need to define ``CONTESTS_URL`` and implement
    ``extract_contests`` and ``extract_contest_info``.
    """

    CONTESTS_URL = None
    TIMEOUT = 30
    # How the fetched body should be parsed: "text", "json" or "html".
    DATA_TYPE = "text"

    # ------------------------------------------------------------------ API

    def update(self, now=None):
        """Scrape the site and replace its stored contests.

        Returns the number of stored contests or 0 when the fetch failed.
        """
        self._current_time = now or timezone.now()
        raw = self.fetch()
        if raw is None:
            logger.warning("%s: fetch failed, leaving stored data untouched", self.site)
            return 0

        data = self.parse(raw)
        contests = self.extract_contests(data) or []

        records = []
        for raw_contest in contests:
            info = self.extract_contest_info(raw_contest)
            if info is not None:
                records.append(info)

        self.replace(records, now=self._current_time)
        return len(records)

    def fetch(self):
        """Return the raw, unparsed representation of the site's page/API."""
        response = requests.get(
            self.CONTESTS_URL,
            headers={"User-Agent": USER_AGENT},
            timeout=self.TIMEOUT,
        )
        response.raise_for_status()
        return response.text

    def parse(self, text):
        """Convert the raw response body into a usable data structure."""
        if self.DATA_TYPE == "json":
            return self.parse_json(text)
        if self.DATA_TYPE == "html":
            return self.parse_html(text)
        return text

    # ------------------------------------------------------------ overrides

    @property
    def site(self):
        raise NotImplementedError

    def extract_contests(self, data):
        raise NotImplementedError

    def extract_contest_info(self, raw):
        raise NotImplementedError

    # --------------------------------------------------------------- helpers

    @staticmethod
    def parse_json(text):
        return json.loads(text)

    @staticmethod
    def parse_html(text):
        return BeautifulSoup(text, "lxml")

    def replace(self, records, now=None):
        now = now or timezone.now()
        with transaction.atomic():
            Contest.objects.filter(site=self.site).delete()
            Contest.objects.bulk_create(
                [Contest(site=self.site, **info) for info in records],
                batch_size=500,
            )
        LastUpdate.objects.update_or_create(site=self.site, defaults={"date": now})

    def build_info(self, **fields):
        """Normalise a raw contest payload into model-ready values.

        ``start_time``/``end_time`` may be naive datetimes (treated as UTC);
        ``duration`` may be ``None`` when the value is unknown.
        """
        start_time = fields.pop("start_time", None)
        end_time = fields.pop("end_time", None)
        status = fields.pop("status", None)
        status = status or guess_status(start_time, now=self._current_time)

        info = {
            "name": fields.pop("name", ""),
            "url": fields.pop("url", ""),
            "start_time": self._to_aware(start_time),
            "end_time": self._to_aware(end_time),
            "duration": self._to_seconds(fields.pop("duration", None)),
            "status": status,
            "in_24_hours": in_24_hours(start_time, status, now=self._current_time)
            == "Yes",
        }
        info.update(fields)
        return info

    @staticmethod
    def _to_aware(value):
        if value is None:
            return None
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value

    @staticmethod
    def _to_seconds(value):
        if value is None:
            return None
        if isinstance(value, timedelta):
            return int(value.total_seconds())
        return int(value)
