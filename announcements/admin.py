from django.contrib import admin
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'priority',
        'is_active',
        'created_by',
        'created_at',
        'expires_at',
    )

    list_filter = (
        'priority',
        'is_active',
        'created_at',
    )

    search_fields = (
        'title',
        'body',
    )

    ordering = ('-created_at',)