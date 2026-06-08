"""Experiences app configuration.

This app owns the `Experience` model (employment history shown at /experiences/).
It has a cross-app M2M dependency on `projects.Technology` via
`Experience.skills`, reusing the existing Technology catalog as the single
source of truth for skill names and icons. See design sdd/experiences-page/design
Decisions & rationale item 1 for rationale.
"""
from django.apps import AppConfig


class ExperiencesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'experiences'
