from django.db import models


class Contest(models.Model):
    """A competitive programming contest scraped from one of the supported sites."""

    site = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)

    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(
        null=True, blank=True, help_text="Duration in seconds."
    )

    status = models.CharField(max_length=10, db_index=True)
    in_24_hours = models.BooleanField(default=False)

    # Site-specific fields (only populated for the sites that expose them).
    difficulty = models.IntegerField(null=True, blank=True)
    rated_range = models.CharField(max_length=100, blank=True, default="")
    type = models.CharField(max_length=20, blank=True, default="")
    is_rated = models.CharField(max_length=5, blank=True, default="")
    is_official = models.CharField(max_length=5, blank=True, default="")

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.site}: {self.name}"


class LastUpdate(models.Model):
    """Tracks the last time each site was successfully scraped."""

    site = models.CharField(max_length=50, unique=True)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.site}: {self.date}"
