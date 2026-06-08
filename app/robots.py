from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_GET


@require_GET
def robots_txt(request):
    body = "\n".join([
        "User-agent: *",
        "Disallow: /admin/",
        "",
        f"Sitemap: {settings.SITE_URL.rstrip('/')}/sitemap.xml",
        "",
    ])
    return HttpResponse(body, content_type="text/plain; charset=utf-8")
