from django.urls import path

from .constants import ACTIVE_SITES
from .views import AllContestsView, SiteContestsView, SitesView

urlpatterns = [
    path("v1/all", AllContestsView.as_view(), name="api_v1_all"),
    path("v1/sites", SitesView.as_view(), name="api_v1_sites"),
]

for _name, key, _url in ACTIVE_SITES:
    urlpatterns.append(
        path(
            f"v1/{key}", SiteContestsView.as_view(), {"site": key}, name=f"api_v1_{key}"
        )
    )
