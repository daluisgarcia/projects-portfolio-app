from datetime import datetime

from django.views.generic import TemplateView

from blog.models import BlogPost

from .models import Project, ProjectField


class LandingView(TemplateView):
    template_name = "projects/landing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_page"] = "landing"
        context["projects"] = (
            Project.objects.filter(is_active=True, pinned=True)
            .prefetch_related("technologies", "tech_fields", "media_files")
            .order_by("-priority", "-year_of_realization")
        )
        context["profile"] = {
            "name": "Daniel Luis",
            "role": "Software Engineer & Data Scientist",
            "vision": "Bridging precision engineering with intelligent systems...",
            "years": f"{datetime.now().year - 2020}+",
        }
        context["blog_posts"] = list(
            BlogPost.objects
            .filter(is_published=True)
            .select_related("category")
            .prefetch_related("tags")
            .order_by("-published_at")[:3]
        )
        return context


class ProjectsView(TemplateView):
    template_name = "projects/projects.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_page"] = "projects"
        context["projects"] = (
            Project.objects.filter(is_active=True)
            .prefetch_related("technologies", "tech_fields", "media_files")
            .order_by("-priority", "-year_of_realization")
        )
        context["categories"] = (
            ProjectField.objects.all().order_by("name")
        )
        return context
