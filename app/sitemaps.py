from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET

from blog.models import BlogPost


STATIC_PATHS = [
    ("/",                  "landing",       None),
    ("/projects/",         "projects",      None),
    ("/experiences/",      "experiences",   None),
    ("/blog/",             "blog_list",     None),
]


@require_GET
def sitemap_xml(request):
    """Serve /sitemap.xml as application/xml.

    No django.contrib.sitemaps (avoids a Site row, a migration, and
    a current_site template tag — the project is single-tenant).
    """
    base = settings.SITE_URL.rstrip("/")
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    now_iso = timezone.now().isoformat()
    for path, _name, _arg in STATIC_PATHS:
        lines.append("  <url>")
        lines.append(f"    <loc>{base}{path}</loc>")
        lines.append(f"    <lastmod>{now_iso}</lastmod>")
        lines.append("  </url>")

    # Categories are intentionally omitted: the canonical blog_list view
    # strips `?category=` via a 301, so listing them here would create
    # sitemap entries that don't match the canonical URL.
    for post in BlogPost.objects.filter(is_published=True).only("slug", "updated_at"):
        lines.append("  <url>")
        lines.append(f"    <loc>{base}{reverse('blog_detail', kwargs={'slug': post.slug})}</loc>")
        lines.append(f"    <lastmod>{post.updated_at.isoformat()}</lastmod>")
        lines.append("  </url>")

    lines.append("</urlset>")
    return HttpResponse("\n".join(lines) + "\n", content_type="application/xml; charset=utf-8")
