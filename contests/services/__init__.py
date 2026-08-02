"""Registry of all site scraper services."""

from .at_coder import AtCoderService
from .code_chef import CodeChefService
from .codeforces import CodeforcesGymService, CodeforcesService
from .cs_academy import CsAcademyService
from .hacker_earth import HackerEarthService
from .hacker_rank import HackerRankService
from .leet_code import LeetCodeService
from .top_coder import TopCoderService
from .toph import TophService

SERVICES = [
    CodeforcesService,
    CodeforcesGymService,
    TopCoderService,
    AtCoderService,
    CsAcademyService,
    CodeChefService,
    HackerRankService,
    HackerEarthService,
    LeetCodeService,
    TophService,
]
