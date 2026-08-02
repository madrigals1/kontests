from datetime import timedelta, timezone

from django.utils import timezone as dj_timezone

from .constants import UNKNOWN

# Shared tzinfo for "no offset" timestamps. Avoids the Django 5 removal of
# ``django.utils.timezone.utc`` in favour of the stdlib object.
UTC = timezone.utc


def utc_format(dt):
    """Format a datetime as %Y-%m-%dT%H:%M:%S.000Z or the UNKNOWN sentinel."""
    if dt is None:
        return UNKNOWN
    if dt.tzinfo is None:
        from datetime import timezone

        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def duration_seconds(value):
    """Return the integer number of seconds or the UNKNOWN sentinel."""
    if value is None:
        return UNKNOWN
    return int(value)


def in_24_hours(start_time, status, now=None):
    """Mirror the original heuristic: a CODING contest is never 'in 24 hours'."""
    if status == "CODING" or start_time is None:
        return "No"
    now = now or dj_timezone.now()
    return "Yes" if (start_time - now) <= timedelta(hours=24) else "No"


def guess_status(start_time, now=None):
    """Contests that already started are considered CODING, otherwise BEFORE."""
    if start_time is None:
        return "BEFORE"
    now = now or dj_timezone.now()
    return "CODING" if start_time <= now else "BEFORE"


def to_bool_flag(value):
    return "Yes" if value else "No"
