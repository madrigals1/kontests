"""Run the periodic contest updater (mirrors the original clock.rb).

Usage:
    python manage.py scheduler
"""

import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from django.core.management.base import BaseCommand

from ...services import (
    AtCoderService,
    CodeChefService,
    CodeforcesGymService,
    CodeforcesService,
    CsAcademyService,
    HackerEarthService,
    HackerRankService,
    LeetCodeService,
    TopCoderService,
    TophService,
)

logger = logging.getLogger(__name__)

# (interval_minutes, services) — matching the upstream cadence.
SCHEDULE = [
    (3, [CodeforcesService, CodeforcesGymService, TopCoderService, AtCoderService]),
    (5, [CodeChefService, HackerRankService, HackerEarthService, LeetCodeService]),
    (7, [CsAcademyService, TophService]),
]


def run(service_classes):
    for service_cls in service_classes:
        service = service_cls()
        try:
            service.update()
        except Exception:
            logger.exception("%s update failed", service.site)


class Command(BaseCommand):
    help = "Continuously refresh contests from the supported sites."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone="UTC")
        for minutes, service_classes in SCHEDULE:
            scheduler.add_job(
                run,
                "interval",
                minutes=minutes,
                args=[service_classes],
                id=f"every_{minutes}_min",
                next_run_time=None,
            )
            for service_cls in service_classes:
                self.stdout.write(
                    f"Scheduled {service_cls.__name__} every {minutes} minutes"
                )
        self.stdout.write("Scheduler started. Press Ctrl+C to stop.")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
