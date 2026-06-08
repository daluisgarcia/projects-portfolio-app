from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from blog.models import BlogPost, Category


# --- SEO tests (Change: seo-overhaul) ---


class ProjectsSeoMetaTests(TestCase):
    """Per-page SEO meta on the landing + projects pages.

    Spec source: sdd/seo-overhaul/design #111 (REQ-SEO-001..004). The same
    base-template SEO scaffolding (meta description, Open Graph, Twitter Card,
    canonical, WebSite + Person JSON-LD) must render on every page; the
    landing and projects pages also set their own ``og:url`` to the absolute
    canonical URL.
    """

    def _assert_seo_present(self, response, expected_title_substring=""):
        body = response.content.decode("utf-8")
        for needle in [
            '<meta name="description"',
            'property="og:title"',
            'property="og:description"',
            'property="og:image"',
            'property="og:url"',
            'property="og:type"',
            'property="og:site_name"',
            'name="twitter:card"',
            'name="twitter:title"',
            'name="twitter:image"',
            'rel="canonical"',
            '"@type":"WebSite"',
            '"@type":"Person"',
        ]:
            self.assertIn(needle, body, f"missing SEO needle: {needle}")
        if expected_title_substring:
            self.assertIn(expected_title_substring, body)

    def test_landing_seo(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self._assert_seo_present(r, expected_title_substring="Daniel Luis")
        # og:url must be the absolute landing URL
        self.assertIn(
            'property="og:url" content="https://daluis.dev/"',
            r.content.decode("utf-8"),
        )

    def test_landing_blog_posts_real(self):
        """Landing should now show real BlogPost rows, not hardcoded link='#' cards."""
        # BlogPost.category is non-null (FK PROTECT) so create a Category first.
        category = Category.objects.create(name="MLOps", slug="mlops")
        BlogPost.objects.create(
            title="Real Post",
            slug="real-post",
            body="x",
            category=category,
            is_published=True,
            published_at=timezone.now(),
        )
        r = self.client.get("/")
        body = r.content.decode("utf-8")
        self.assertIn('href="/blog/real-post/"', body)
        self.assertNotIn('href="#">', body)  # no fake hardcoded links

    def test_projects_seo(self):
        r = self.client.get(reverse("projects"))
        self.assertEqual(r.status_code, 200)
        self._assert_seo_present(r, expected_title_substring="Projects")
        self.assertIn(
            'property="og:url" content="https://daluis.dev/projects/"',
            r.content.decode("utf-8"),
        )
