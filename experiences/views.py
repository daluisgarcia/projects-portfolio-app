# views.py — CBV for the public /experiences/ page
from django.views.generic import TemplateView

from .models import Experience


class ExperienceListView(TemplateView):
    """Public timeline of professional experiences.

    Pulls all active experiences, prefetches M2M `skills` to avoid N+1
    (2 queries total: one for experiences, one IN-batch for skills).
    Orders by manual display_order first (low number = higher on page),
    then by priority (quality/relevance, high first), then by recency.
    """

    template_name = "experiences/list.html"

    def get_context_data(self, **kwargs):
        # Set active_page for nav highlight in base.html
        context = super().get_context_data(**kwargs)
        context["active_page"] = "experience"
        context["experiences"] = (
            Experience.objects
            .filter(is_active=True)
            .prefetch_related("skills")
            .order_by("display_order", "-priority", "-start_date")
        )
        return context
