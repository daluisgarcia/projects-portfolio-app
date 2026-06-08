from datetime import datetime

from django.views.generic import TemplateView

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
        context["blog_posts"] = [
            {
                "title": "Designing Resilient ML Pipelines",
                "date": "Mar 2026",
                "image_url": "https://via.placeholder.com/800x450/051424/ffb599?text=ML+Pipelines",
                "excerpt": "Lessons learned from deploying ML systems at scale...",
                "link": "#",
            },
            {
                "title": "The Art of Data Modeling",
                "date": "Feb 2026",
                "image_url": "https://via.placeholder.com/800x450/051424/ffb599?text=Data+Modeling",
                "excerpt": "How thoughtful data modeling reduces downstream complexity...",
                "link": "#",
            },
            {
                "title": "Building Trustworthy AI Systems",
                "date": "Jan 2026",
                "image_url": "https://via.placeholder.com/800x450/051424/ffb599?text=Trustworthy+AI",
                "excerpt": "A framework for building AI systems that earn user trust...",
                "link": "#",
            },
        ]
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
