from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from contests.views import ApiIndexView

urlpatterns = [
    # The root of the site points developers at the API.
    path("", RedirectView.as_view(url="/api/", permanent=False)),
    path("api/", ApiIndexView.as_view()),
    path("api/", include("contests.urls")),
    path("admin/", admin.site.urls),
]
