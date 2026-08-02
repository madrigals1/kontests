"""Codeforces (regular contests) scraper."""
from datetime import datetime, timedelta

from ..constants import CODEFORCES_ACTIVE_PHASES
from ..utils import UTC
from .base import BaseService


class CodeforcesBaseService(BaseService):
    """Shared parsing logic between Codeforces and Codeforces::Gym."""

    def extract_contests(self, data):
        contests = data["result"]
        return [
            contest
            for contest in reversed(contests)
            if contest["phase"] in CODEFORCES_ACTIVE_PHASES
        ]

    def extract_contest_info(self, contest):
        contest_id = contest["id"]
        duration = contest.get("durationSeconds")
        phase = contest["phase"]

        start = None
        end = None
        if contest.get("startTimeSeconds"):
            start = datetime.fromtimestamp(
                contest["startTimeSeconds"], tz=UTC
            )
            end = start + timedelta(seconds=duration)

        return self.build_info(
            name=contest["name"],
            url=self.contest_url(contest_id),
            start_time=start,
            end_time=end,
            duration=duration,
            status=phase,
        )

    def contest_url(self, contest_id):
        raise NotImplementedError


class CodeforcesService(CodeforcesBaseService):
    CONTESTS_URL = "https://codeforces.com/api/contest.list"
    DATA_TYPE = "json"

    @property
    def site(self):
        return "codeforces"

    def contest_url(self, contest_id):
        return f"https://codeforces.com/contestRegistration/{contest_id}"


class CodeforcesGymService(CodeforcesBaseService):
    CONTESTS_URL = "https://codeforces.com/api/contest.list?gym=true"
    DATA_TYPE = "json"

    @property
    def site(self):
        return "codeforces_gym"

    def contest_url(self, contest_id):
        return f"https://codeforces.com/gymRegistration/{contest_id}"

    def extract_contest_info(self, contest):
        info = super().extract_contest_info(contest)
        info["difficulty"] = contest.get("difficulty") or 0
        return info
