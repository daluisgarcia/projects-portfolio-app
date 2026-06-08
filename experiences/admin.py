# admin.py — Django admin registration for the Experience model
from django.contrib import admin

from .models import Experience


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    """Admin for the Experience model — registered experiences shown on the public timeline page."""

    list_display = (
        "role_title",
        "company",
        "start_date",
        "end_date",
        "is_active",
        "priority",
        "display_order",
        "accent_style",
    )
    list_filter = ("is_active", "accent_style")
    search_fields = ("company", "role_title", "description")
    filter_horizontal = ("skills",)  # M2M widget for selecting existing Technology rows
    ordering = ("display_order", "-priority", "-start_date")
    date_hierarchy = "start_date"
    list_per_page = 25
