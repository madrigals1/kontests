"""Fetch the latest contests from the supported sites.

Usage:
    python manage.py update_contests
    python manage.py update_contests --sites codeforces at_coder
"""

import logging

from django.core.management.base import BaseCommand

from ...services import SERVICES

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Update contests for all (or selected) supported sites."

    def add_arguments(self, parser):
        parser.add_argument(
            "--sites",
            nargs="*",
            dest="sites",
            default=None,
            help="Space-separated site keys to update (default: all sites).",
        )

    def handle(self, *args, **options):
        requested = set(options["sites"]) if options["sites"] else None
        services = [
            service_cls()
            for service_cls in SERVICES
            if requested is None or service_cls().site in requested
        ]

        if not services:
            self.stderr.write("No matching sites to update.")
            return

        for service in services:
            try:
                count = service.update()
                self.stdout.write(f"{service.site}: stored {count} contests")
            except Exception as exc:  # keep going on individual site failures
                logger.exception("%s failed", service.site)
                self.stderr.write(f"{service.site}: failed ({exc})")
