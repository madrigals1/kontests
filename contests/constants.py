from datetime import timedelta

SITES = [
    ("All", "all", "https://kontests.net"),
    ("CodeForces", "codeforces", "https://codeforces.com"),
    ("CodeForces::Gym", "codeforces_gym", "https://codeforces.com/gyms"),
    ("TopCoder", "top_coder", "https://topcoder.com"),
    ("AtCoder", "at_coder", "https://atcoder.jp"),
    ("CS Academy", "cs_academy", "https://csacademy.com"),
    ("CodeChef", "code_chef", "https://codechef.com"),
    ("HackerRank", "hacker_rank", "https://hackerrank.com"),
    ("HackerEarth", "hacker_earth", "https://hackerearth.com"),
    ("LeetCode", "leet_code", "https://leetcode.com"),
    ("Toph", "toph", "https://toph.co"),
]

# Sites whose contests are actually fetched. Keep this aligned with SITES
# (the first "All" entry is only a convenience and never fetched directly).
ACTIVE_SITES = [site for site in SITES[1:]]

STATUS_BEFORE = "BEFORE"
STATUS_CODING = "CODING"

# Statuses reported by Codeforces for contests we want to keep.
CODEFORCES_ACTIVE_PHASES = frozenset({"BEFORE", "CODING"})

# Sentinel used to render "unknown" values, mirroring the original app.
UNKNOWN = "-"

# The upstream format used for timestamps, e.g. 2021-01-01T00:00:00.000Z
UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.%LZ"
