"""Blog app configuration.

Self-contained blog app — no cross-app FKs. Models: Category, Tag, BlogPost.
"""
from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "blog"
