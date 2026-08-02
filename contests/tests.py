import json
from datetime import datetime, timedelta

from django.test import TestCase
from rest_framework.test import APIClient

from .models import Contest, LastUpdate
from .services import CodeChefService, CodeforcesService, LeetCodeService, TophService
from .utils import UTC


def json_fetch(payload):
    return lambda: json.dumps(payload)


class ContestFixtures:
    @staticmethod
    def codeforces():
        return {
            "result": [
                {
                    "name": "Codeforces Round #146",
                    "id": 146,
                    "phase": "FINISHED",
                    "startTimeSeconds": 1320000000,
                    "durationSeconds": 7200,
                },
                {
                    "name": "Codeforces Round #147",
                    "id": 147,
                    "phase": "CODING",
                    "startTimeSeconds": 1320100000,
                    "durationSeconds": 7200,
                },
            ]
        }

    @staticmethod
    def leetcode():
        return {"data": {"allContests": [{"title": "Biweekly 1", "titleSlug": "bw1", "startTime": 1600000000, "duration": 5400}]}}

    @staticmethod
    def codechef():
        return {
            "present_contests": [],
            "future_contests": [
                {
                    "contest_name": "Long Challenge",
                    "contest_code": "LTIME1",
                    "contest_duration": "180",
                    "contest_start_date_iso": "2030-01-01T10:00:00+00:00",
                    "contest_end_date_iso": "2030-01-01T13:00:00+00:00",
                }
            ],
        }


class CodeforcesServiceTests(TestCase):
    def test_extract_filters_inactive_phases(self):
        service = CodeforcesService()
        service._current_time = datetime(2030, 1, 1, tzinfo=UTC)
        contests = service.extract_contests(ContestFixtures.codeforces())
        self.assertEqual(len(contests), 1)
        self.assertEqual(contests[0]["id"], 147)  # FINISHED filtered out

    def test_update_stores_only_active_contests(self):
        service = CodeforcesService()
        service.fetch = json_fetch(ContestFixtures.codeforces())  # type: ignore[assignment]
        service._current_time = datetime(2030, 1, 1, tzinfo=UTC)
        count = service.update()
        self.assertEqual(count, 1)
        self.assertEqual(Contest.objects.filter(site="codeforces").count(), 1)
        self.assertEqual(LastUpdate.objects.get(site="codeforces").site, "codeforces")


class LeetCodeServiceTests(TestCase):
    def test_update_skips_finished_contests(self):
        service = LeetCodeService()
        service.fetch = json_fetch(ContestFixtures.leetcode())  # type: ignore[assignment]
        service._current_time = datetime(2030, 1, 1, tzinfo=UTC)
        count = service.update()
        self.assertEqual(count, 0)


class CodeChefServiceTests(TestCase):
    def test_update_parses_duration(self):
        service = CodeChefService()
        service.fetch = json_fetch(ContestFixtures.codechef())  # type: ignore[assignment]
        service._current_time = datetime(2030, 1, 1, tzinfo=UTC)
        count = service.update()
        self.assertEqual(count, 1)
        contest = Contest.objects.get(site="code_chef")
        self.assertEqual(contest.duration, 10800)


class AllContestsViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        future = datetime(2030, 1, 2, tzinfo=UTC)
        Contest.objects.create(
            site="codeforces",
            name="CF Future",
            url="https://codeforces.com/contestRegistration/1",
            start_time=future + timedelta(hours=1),
            end_time=future + timedelta(hours=3),
            duration=7200,
            status="BEFORE",
            in_24_hours=False,
        )
        past = datetime(2020, 1, 1, tzinfo=UTC)
        Contest.objects.create(
            site="at_coder",
            name="AtCoder Past",
            url="https://atcoder.jp/contests/abc001",
            start_time=past,
            end_time=past + timedelta(hours=2),
            duration=7200,
            status="CODING",
            in_24_hours=False,
            rated_range="Beginner",
        )

    def test_all_endpoint_orders_and_serializes(self):
        response = self.client.get("/api/v1/all")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["site"], "at_coder")
        self.assertEqual(data[0]["start_time"], "2020-01-01T00:00:00.000Z")
        self.assertEqual(data[0]["status"], "CODING")
        self.assertIn("site", data[0])

    def test_site_endpoint_shape(self):
        response = self.client.get("/api/v1/codeforces")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertNotIn("site", data[0])
        self.assertEqual(data[0]["in_24_hours"], "No")

    def test_atcoder_rated_range(self):
        response = self.client.get("/api/v1/at_coder")
        data = response.json()
        self.assertEqual(data[0]["rated_range"], "Beginner")

    def test_sites_endpoint(self):
        response = self.client.get("/api/v1/sites")
        data = response.json()
        # "All" is excluded from the supported sites list, matching the upstream.
        self.assertEqual(data[0], ["CodeForces", "codeforces", "https://codeforces.com"])
        self.assertEqual(data[-1], ["Toph", "toph", "https://toph.co"])


class TophServiceTests(TestCase):
    HTML = """
    <html><body>
    <div class="container"><div class="row"><div class="col-md-9">
      <div class="panel"><div class="caption"><h2>Old placeholder</h2></div></div>
    </div></div></div>
    <div class="container"><div class="row"><div class="col-md-9">
      <div class="panel"><div class="caption"><h2>Contest A</h2>
        <a href="/contests/a"></a>
      </div><span class="timestamp" data-time="1893456000">x</span></div>
      <div class="panel"><div class="caption"><h2>No timestamp</h2></div></div>
    </div></div></div>
    </body></html>
    """

    def test_extract_returns_panels_from_second_container(self):
        service = TophService()
        service._current_time = datetime(2030, 1, 1, tzinfo=UTC)
        soup = service.parse_html(self.HTML)
        panels = service.extract_contests(soup)
        self.assertEqual(len(panels), 2)
        # Only the panel with a timestamp yields a contest.
        info = [service.extract_contest_info(p) for p in panels]
        info = [i for i in info if i is not None]
        self.assertEqual(len(info), 1)
        self.assertEqual(info[0]["name"], "Contest A")
