"""Serializers producing the exact output shape of the original kontests API."""

from rest_framework import serializers

from .utils import duration_seconds, to_bool_flag, utc_format


class ContestSerializer(serializers.Serializer):
    """Base serializer with the fields shared by every site."""

    name = serializers.CharField()
    url = serializers.CharField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    in_24_hours = serializers.SerializerMethodField()
    status = serializers.CharField()

    def get_start_time(self, obj):
        return utc_format(obj.start_time)

    def get_end_time(self, obj):
        return utc_format(obj.end_time)

    def get_duration(self, obj):
        return duration_seconds(obj.duration)

    def get_in_24_hours(self, obj):
        return to_bool_flag(obj.in_24_hours)


class CodeforcesSerializer(ContestSerializer):
    pass


class CodeforcesGymSerializer(ContestSerializer):
    difficulty = serializers.IntegerField()


class TopCoderSerializer(ContestSerializer):
    pass


class AtCoderSerializer(ContestSerializer):
    rated_range = serializers.CharField()


class CsAcademySerializer(ContestSerializer):
    pass


class CodeChefSerializer(ContestSerializer):
    pass


class HackerRankSerializer(ContestSerializer):
    type_ = serializers.CharField(source="type")


class HackerEarthSerializer(ContestSerializer):
    type_ = serializers.CharField(source="type")


class LeetCodeSerializer(ContestSerializer):
    pass


class TophSerializer(ContestSerializer):
    is_rated = serializers.CharField()
    is_official = serializers.CharField()


class AllContestsSerializer(ContestSerializer):
    site = serializers.CharField()


# Map each site key to the serializer used by its endpoint.
SITE_SERIALIZERS = {
    "codeforces": CodeforcesSerializer,
    "codeforces_gym": CodeforcesGymSerializer,
    "top_coder": TopCoderSerializer,
    "at_coder": AtCoderSerializer,
    "cs_academy": CsAcademySerializer,
    "code_chef": CodeChefSerializer,
    "hacker_rank": HackerRankSerializer,
    "hacker_earth": HackerEarthSerializer,
    "leet_code": LeetCodeSerializer,
    "toph": TophSerializer,
}
