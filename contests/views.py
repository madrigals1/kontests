"""API views exposing the scraped contests, mirroring the original endpoints."""

from datetime import timedelta

from django.db.models import F
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from .constants import ACTIVE_SITES
from .models import Contest
from .serializers import SITE_SERIALIZERS, AllContestsSerializer


class ApiIndexView(APIView):
    """GET /api — lists the available contest endpoints."""

    def get(self, request):
        sites = [
            {
                "name": name,
                "endpoint": reverse(f"api_v1_{key}", request=request),
            }
            for name, key, _ in ACTIVE_SITES
        ]
        return Response(
            {
                "endpoints": {
                    "all": reverse("api_v1_all", request=request),
                    "coming": reverse("api_v1_coming", request=request),
                    "sites": reverse("api_v1_sites", request=request),
                },
                "sites": sites,
            }
        )


class AllContestsView(APIView):
    """GET /api/v1/all — every contest across all supported sites."""

    def get(self, request):
        queryset = Contest.objects.order_by(F("start_time").asc(nulls_last=True))
        return Response(AllContestsSerializer(queryset, many=True).data)


class SiteContestsView(APIView):
    """GET /api/v1/<site> — the contests for one site."""

    def get(self, request, site):
        serializer_class = SITE_SERIALIZERS.get(site)
        if serializer_class is None:
            return Response({"error": f"Unsupported site: {site}"}, status=404)

        queryset = Contest.objects.filter(site=site).order_by(
            F("start_time").asc(nulls_last=True)
        )
        return Response(serializer_class(queryset, many=True).data)


class ComingContestsView(APIView):
    """GET /api/v1/coming — contests starting in the next 24 hours.

    Unlike the stored ``in_24_hours`` flag (which goes stale between scrapes),
    this is computed at request time so it stays accurate when polled every
    few minutes.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        now = timezone.now()
        window_end = now + timedelta(hours=24)
        queryset = Contest.objects.filter(
            start_time__gte=now, start_time__lte=window_end
        ).order_by(F("start_time").asc(nulls_last=True))
        return Response(AllContestsSerializer(queryset, many=True).data)


class SitesView(APIView):
    """GET /api/v1/sites — the list of supported sites."""

    def get(self, request):
        return Response([list(site) for site in ACTIVE_SITES])
