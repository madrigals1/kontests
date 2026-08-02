from django.contrib import admin

from .models import Contest, LastUpdate


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ("site", "name", "start_time", "end_time", "duration", "status")
    list_filter = ("site", "status")
    search_fields = ("name", "url")


@admin.register(LastUpdate)
class LastUpdateAdmin(admin.ModelAdmin):
    list_display = ("site", "date")
