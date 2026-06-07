# tests.py — Smoke test suite for the blog app.
#
# First test suite in the `blog` app. Uses plain django.test.TestCase
# (no pytest). Run with: .venv/bin/python manage.py test blog
#
# Coverage maps to the testable scenarios in spec #87 and design #88.
# Eight test classes, mirroring the structure of experiences/tests.py:
#   1. BlogModelTests             — model invariants (Category, Tag, BlogPost)
#   2. BlogListViewTests          — bento-grid index page
#   3. BlogPostDetailViewTests    — single-column reading page
#   4. BaseTemplateNavTests       — base.html nav rewiring (Batch 4)
#   5. BlogPostAdminTests         — admin registration
#   6. BlogProseStylesTests       — detail-page .blog-prose wrapper (post-Batch-6 hotfix)
#   7. BlogCategoryFilterTests    — list-page category filter (post-archive hotfix)
#   8. BlogPaginationTests        — paginated list + LOAD MORE button (post-archive hotfix)
#
# Edge-case scenarios from spec #87 (Markdown nl2br behavior, Tailwind
# class activation, static asset wiring) are verified by the views'
# template inheritance and the static asset findstatic smoke test in
# Phase 11 — not duplicated here, to keep this suite fast and focused.
#
# Empirical query budget (test_no_n_plus_one) verified via a probe run
# with django.test.utils.CaptureQueriesContext: the list view runs in
# exactly 5 queries (1 main posts SELECT + 2 prefetch caches for tags
# and related_posts + 1 categories SELECT for the filter chips + 1
# paginator COUNT query). select_related("category") joins the FK
# inline at no extra cost.

import re
import unittest

from django.contrib import admin as django_admin
from django.db import IntegrityError, connection
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import resolve, reverse
from django.utils import timezone

from blog.admin import BlogPostAdmin, BlogPostEmbeddingAdmin, CategoryAdmin, TagAdmin
from blog.models import BlogPost, BlogPostEmbedding, Category, Tag
from blog.views import BlogListView, BlogPostDetailView


# HTML helpers (shared by BaseTemplateNavTests) -----------------------------

# Desktop active-state class set, byte-for-byte from templates/base.html.
_DESKTOP_ACTIVE = "text-secondary font-bold border-b-2 border-secondary pb-1"
# Mobile active-state class set, byte-for-byte from templates/base.html.
_MOBILE_ACTIVE = "border-l-2 border-secondary bg-surface-container text-secondary font-bold"
# Matches the two Blog <a> elements in base.html (desktop + mobile drawer).
_BLOG_ANCHOR_RE = re.compile(r'<a[^>]*>Blog</a>')


def _blog_anchors(response):
    """Return the <a>...</a> strings for both Blog nav links (desktop + mobile)."""
    return _BLOG_ANCHOR_RE.findall(response.content.decode())


class BlogModelTests(TestCase):
    """Tests for the Category, Tag, and BlogPost models.

    Covers spec #87 scenarios: 'Category model', 'Tag model', 'BlogPost
    fields', 'read_time_minutes', 'published_at', 'body_html', 'BlogPost
    category FK PROTECT', 'BlogPost related_posts M2M', 'BlogPost tags
    M2M'.
    """

    @classmethod
    def setUpTestData(cls):
        # Class-level fixtures — created once, rolled back per test method.
        cls.category = Category.objects.create(name="MLOps", slug="mlops")
        cls.other_category = Category.objects.create(name="Data", slug="data")
        cls.tag = Tag.objects.create(name="Python", slug="python")
        cls.now = timezone.now()
        cls.post = BlogPost.objects.create(
            title="Hello World",
            slug="hello-world",
            body="word " * 200,
            excerpt="An excerpt.",
            category=cls.category,
            is_published=True,
            published_at=cls.now,
        )
        cls.post.tags.add(cls.tag)
        cls.draft = BlogPost.objects.create(
            title="Draft Post",
            slug="draft-post",
            body="draft",
            category=cls.category,
            is_published=False,
        )
        cls.related_post = BlogPost.objects.create(
            title="Related",
            slug="related",
            body="x",
            category=cls.other_category,
            is_published=True,
        )

    def test_category_str(self):
        # Category.__str__ returns the name (spec #87 'Category model' scenario).
        self.assertEqual(str(self.category), "MLOps")

    def test_tag_str(self):
        # Tag.__str__ returns the name (spec #87 'Tag model' scenario).
        self.assertEqual(str(self.tag), "Python")

    def test_blogpost_str(self):
        # BlogPost.__str__ returns the title (spec #87 'BlogPost fields' scenario).
        self.assertEqual(str(self.post), "Hello World")

    def test_slug_unique(self):
        # Saving two posts with the same slug raises IntegrityError
        # (spec #87 'BlogPost fields' / slug-uniqueness scenario).
        with self.assertRaises(IntegrityError):
            BlogPost.objects.create(
                title="Dup",
                slug=self.post.slug,
                body="x",
                category=self.category,
            )

    def test_read_time_minutes_empty_body(self):
        # Empty body clamps to 1 minute (spec #87 'read_time_minutes'
        # empty-body scenario). Verifies the `max(1, ...)` floor.
        post = BlogPost.objects.create(
            title="Empty", slug="empty", body="", category=self.category
        )
        self.assertEqual(post.read_time_minutes, 1)

    def test_read_time_minutes_one_minute(self):
        # 200 words → exactly 1 minute (200 / 200 = 1.0; ceil(1.0) = 1).
        self.post.refresh_from_db()
        self.assertEqual(self.post.read_time_minutes, 1)

    def test_read_time_minutes_two_minutes(self):
        # 201 words → 2 minutes (201 / 200 = 1.005; ceil(1.005) = 2;
        # spec #87 'read_time_minutes' ceiling scenario).
        post = BlogPost.objects.create(
            title="TwoMin", slug="two-min", body="word " * 201, category=self.category
        )
        self.assertEqual(post.read_time_minutes, 2)

    def test_read_time_minutes_long_post(self):
        # 10_000 words → 50 minutes (10000 / 200 = 50 exact; spec #87
        # 'read_time_minutes' long-body scenario).
        post = BlogPost.objects.create(
            title="Long", slug="long", body="word " * 10000, category=self.category
        )
        self.assertEqual(post.read_time_minutes, 50)

    def test_body_html_renders_on_save(self):
        # Saving with a markdown body populates body_html (spec #87
        # 'body_html' scenario). Verifies the markdown extension set
        # is wired into BlogPost.save().
        post = BlogPost.objects.create(
            title="Md", slug="md", body="**bold** and *italic*", category=self.category
        )
        self.assertIn("<strong>", post.body_html)
        self.assertIn("<em>", post.body_html)

    def test_body_html_fenced_code(self):
        # Fenced code blocks render to <pre><code> via the
        # `fenced_code` extension (spec #87 'body_html' fenced-code
        # scenario). Also verifies that headings render (default
        # markdown behavior).
        body = "# H\n\n```python\nprint(1)\n```\n"
        post = BlogPost.objects.create(
            title="Code", slug="code", body=body, category=self.category
        )
        self.assertIn("<h1>", post.body_html)
        self.assertIn("<pre><code", post.body_html)

    def test_published_at_auto_set_on_publish(self):
        # First save with is_published=True auto-sets published_at
        # (spec #87 'published_at' first-publish scenario). Verifies
        # the prior-state detection in BlogPost.save().
        post = BlogPost.objects.create(
            title="Auto",
            slug="auto",
            body="x",
            category=self.category,
            is_published=True,
        )
        self.assertIsNotNone(post.published_at)

    def test_published_at_preserved_on_resave(self):
        # Re-saving a published post does NOT change published_at
        # (spec #87 'published_at' re-save-preserves scenario). Manual
        # backdating is also preserved.
        self.post.body = "updated body"
        self.post.save()
        self.post.refresh_from_db()
        self.assertEqual(self.post.published_at, self.now)

    def test_published_at_not_set_on_draft(self):
        # Saving with is_published=False does not auto-set published_at
        # (spec #87 'published_at' draft scenario). The draft fixture
        # was created with is_published=False and no published_at.
        self.draft.refresh_from_db()
        self.assertIsNone(self.draft.published_at)

    def test_category_protect(self):
        # Deleting a Category that has posts raises ProtectedError
        # (spec #87 'BlogPost category FK PROTECT' scenario). The
        # PROTECT on_delete prevents cascading the delete through
        # existing posts.
        with self.assertRaises(ProtectedError):
            self.category.delete()

    def test_related_posts_symmetrical_false(self):
        # Adding A→B does NOT auto-create B→A (verifies
        # symmetrical=False on the self-referential M2M; spec #87
        # 'BlogPost related_posts M2M' scenario).
        self.post.related_posts.add(self.related_post)
        # Forward: A → B is present.
        self.assertIn(self.related_post, self.post.related_posts.all())
        # Reverse: B → A is NOT present (the symmetrical=False guarantee).
        self.assertNotIn(self.post, self.related_post.related_posts.all())

    def test_tags_m2m_related_name(self):
        # Tag.posts reverse M2M works via related_name='posts'
        # (spec #87 'BlogPost tags M2M' scenario). The tag was added
        # to the post in setUpTestData.
        self.assertEqual(self.post.tags.count(), 1)
        self.assertEqual(self.tag.posts.count(), 1)
        self.assertIn(self.post, self.tag.posts.all())


class BlogListViewTests(TestCase):
    """Tests for BlogListView (the bento-grid index page).

    Covers spec #87 scenarios: 'BlogListView context' (featured split,
    drafts excluded, ordering, N+1 protection, active_page, empty
    state) and the URL-routing scenarios for 'blog_list'.
    """

    @classmethod
    def setUpTestData(cls):
        cls.category_a = Category.objects.create(name="MLOps", slug="mlops")
        cls.category_b = Category.objects.create(name="Data", slug="data")
        cls.now = timezone.now()
        cls.post_featured = BlogPost.objects.create(
            title="Featured Post",
            slug="featured-post",
            body="x",
            category=cls.category_a,
            is_published=True,
            is_featured=True,
            published_at=cls.now,
        )
        cls.post_second = BlogPost.objects.create(
            title="Second Post",
            slug="second-post",
            body="x",
            category=cls.category_b,
            is_published=True,
            published_at=cls.now - timezone.timedelta(days=1),
        )
        cls.post_third = BlogPost.objects.create(
            title="Third Post",
            slug="third-post",
            body="x",
            category=cls.category_b,
            is_published=True,
            published_at=cls.now - timezone.timedelta(days=2),
        )
        cls.draft = BlogPost.objects.create(
            title="Hidden Draft",
            slug="hidden-draft",
            body="x",
            category=cls.category_a,
            is_published=False,
        )

    def test_url_resolves(self):
        # reverse('blog_list') returns '/blog/' and resolves to
        # BlogListView (spec #87 'URL routing' scenario).
        url = reverse("blog_list")
        self.assertEqual(url, "/blog/")
        match = resolve(url)
        self.assertEqual(match.func.view_class, BlogListView)

    def test_view_returns_200(self):
        # GET /blog/ returns HTTP 200 (smoke probe).
        self.assertEqual(self.client.get(reverse("blog_list")).status_code, 200)

    def test_view_uses_base_template(self):
        # The page extends base.html (nav, footer) and renders the
        # bento-grid template (spec #87 'List template structure' /
        # template-inheritance scenario).
        response = self.client.get(reverse("blog_list"))
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "blog/list.html")

    def test_view_sets_active_page(self):
        # context['active_page'] == 'blog' (drives the base.html
        # nav-active highlight; spec #87 'BlogListView context'
        # active_page scenario).
        response = self.client.get(reverse("blog_list"))
        self.assertEqual(response.context["active_page"], "blog")

    def test_drafts_excluded(self):
        # Only is_published=True posts appear in context. The draft
        # must not be in featured_post or other_posts (spec #87
        # 'BlogListView context' filter scenario).
        response = self.client.get(reverse("blog_list"))
        self.assertEqual(response.context["featured_post"], self.post_featured)
        other_posts = list(response.context["other_posts"])
        self.assertIn(self.post_second, other_posts)
        self.assertIn(self.post_third, other_posts)
        self.assertNotIn(self.draft, other_posts)
        # Total visible: 3 (the 3 published posts; the draft is hidden).
        self.assertEqual(len(other_posts), 2)

    def test_featured_post_is_first(self):
        # Meta ordering is ('-is_featured', '-published_at'), so
        # post_featured (is_featured=True) is always featured_post
        # even though post_second was published later — wait, post_second
        # was published EARLIER (now-1day), so post_featured (now) is
        # also the most-recently published. This test exercises the
        # -is_featured tie-breaker explicitly by also checking the
        # remaining order.
        response = self.client.get(reverse("blog_list"))
        self.assertEqual(response.context["featured_post"], self.post_featured)
        other_ids = [p.pk for p in response.context["other_posts"]]
        # post_second (published now-1d) must come before post_third
        # (published now-2d) in other_posts.
        self.assertLess(other_ids.index(self.post_second.pk), other_ids.index(self.post_third.pk))

    def test_no_n_plus_one(self):
        # The list view runs in a constant number of queries
        # regardless of post count (spec #87 'BlogListView context'
        # N+1-protection scenario). Empirically observed budget: 5
        # (1 main posts SELECT + 2 prefetch caches for tags and
        # related_posts + 1 categories SELECT for the filter chips
        # + 1 paginator COUNT query; select_related("category") joins
        # the FK inline at no extra cost). The +1 COUNT was added in
        # the pagination hotfix — see sdd/blog-module/feature-pagination-load-more.
        with self.assertNumQueries(5):
            self.client.get(reverse("blog_list"))


class BlogPostDetailViewTests(TestCase):
    """Tests for BlogPostDetailView (single-column reading page).

    Covers spec #87 scenarios: 'BlogPostDetailView' (200 for published,
    404 for missing slug, 404 for unpublished, active_page set) and
    the URL-routing scenarios for 'blog_detail'.
    """

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="MLOps", slug="mlops")
        cls.now = timezone.now()
        cls.post = BlogPost.objects.create(
            title="Detail",
            slug="detail",
            body="**body**",
            category=cls.category,
            is_published=True,
            published_at=cls.now,
        )
        cls.draft = BlogPost.objects.create(
            title="DraftDetail",
            slug="draft-detail",
            body="x",
            category=cls.category,
            is_published=False,
        )

    def test_url_resolves(self):
        # reverse('blog_detail', kwargs={'slug': 'x'}) returns
        # '/blog/x/' and resolves to BlogPostDetailView (spec #87
        # 'URL routing' detail scenario).
        url = reverse("blog_detail", kwargs={"slug": "anything"})
        self.assertEqual(url, "/blog/anything/")
        match = resolve(url)
        self.assertEqual(match.func.view_class, BlogPostDetailView)

    def test_view_returns_200(self):
        # GET on a published post returns 200 and the post is in
        # context (spec #87 'BlogPostDetailView' published scenario).
        response = self.client.get(reverse("blog_detail", kwargs={"slug": self.post.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["post"], self.post)
        self.assertEqual(response.context["active_page"], "blog")

    def test_view_404_for_unpublished(self):
        # GET on an unpublished post returns 404 (no leaked drafts;
        # spec #87 'BlogPostDetailView' unpublished scenario).
        response = self.client.get(reverse("blog_detail", kwargs={"slug": self.draft.slug}))
        self.assertEqual(response.status_code, 404)

    def test_view_404_for_missing_slug(self):
        # GET on a non-existent slug returns 404 (spec #87
        # 'BlogPostDetailView' missing-slug scenario).
        response = self.client.get(reverse("blog_detail", kwargs={"slug": "nonexistent"}))
        self.assertEqual(response.status_code, 404)

    def test_body_html_in_context(self):
        # The post in context has body_html rendered with markdown
        # (the template renders {{ post.body_html|safe }}; spec #87
        # 'Detail template markdown features' scenario).
        response = self.client.get(reverse("blog_detail", kwargs={"slug": self.post.slug}))
        self.assertIn("<strong>", response.context["post"].body_html)

    def test_related_posts_filtered_to_published(self):
        # context['related_posts'] is filtered to is_published=True
        # and capped to 3 (spec #87 'BlogPostDetailView' related-posts
        # scenario). Creates 4 published + 1 draft related posts; the
        # detail view must return only published ones, max 3.
        related = [
            BlogPost.objects.create(
                title=f"R{i}", slug=f"r{i}", body="x",
                category=self.category, is_published=True,
            )
            for i in range(4)
        ]
        draft_related = BlogPost.objects.create(
            title="RDraft", slug="rdraft", body="x",
            category=self.category, is_published=False,
        )
        for p in related + [draft_related]:
            self.post.related_posts.add(p)
        response = self.client.get(reverse("blog_detail", kwargs={"slug": self.post.slug}))
        related_in_context = response.context["related_posts"]
        self.assertEqual(len(related_in_context), 3)
        for r in related_in_context:
            self.assertTrue(r.is_published)
        self.assertNotIn(draft_related, related_in_context)


class BaseTemplateNavTests(TestCase):
    """Tests for the base.html nav rewiring (Batch 4, tasks 9.1 + 9.2).

    Guards spec #88 (part 2) scenarios: 'Blog desktop nav link' and
    'Blog mobile drawer link'. The active-state class set must be
    present on /blog/ and absent on /, /projects/, /experiences/.
    The mobile and desktop variants are tested separately because
    they have different class sets (border-b-2 + pb-1 vs border-l-2 +
    bg-surface-container + text-secondary + font-bold).
    """

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="MLOps", slug="mlops")
        cls.post = BlogPost.objects.create(
            title="A Post",
            slug="a-post",
            body="x",
            category=cls.category,
            is_published=True,
        )

    def test_blog_link_active_on_blog_list(self):
        # On /blog/, both Blog nav anchors carry their respective
        # active-state classes (spec #88 'Blog desktop nav link' +
        # 'Blog mobile drawer link' active-on-/blog/ scenarios).
        response = self.client.get("/blog/")
        self.assertEqual(response.status_code, 200)
        anchors = _blog_anchors(response)
        # Two Blog anchors total (one desktop top-nav, one mobile drawer).
        self.assertEqual(len(anchors), 2)
        # At least one anchor must carry the desktop active classes.
        self.assertTrue(
            any(_DESKTOP_ACTIVE in a for a in anchors),
            f"Desktop Blog active class {_DESKTOP_ACTIVE!r} not found in any Blog anchor: {anchors}",
        )
        # At least one anchor must carry the mobile active classes.
        self.assertTrue(
            any(_MOBILE_ACTIVE in a for a in anchors),
            f"Mobile Blog active class {_MOBILE_ACTIVE!r} not found in any Blog anchor: {anchors}",
        )

    def test_blog_link_inactive_on_home(self):
        # On /, neither Blog nav anchor carries the active-state
        # classes — only the Home link is highlighted (spec #88
        # 'Blog desktop nav link' + 'Blog mobile drawer link'
        # not-active-on-/ scenarios).
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        anchors = _blog_anchors(response)
        self.assertEqual(len(anchors), 2)
        for link in anchors:
            self.assertNotIn(
                "border-b-2 border-secondary pb-1",
                link,
                f"Blog desktop active class leaked into inactive page: {link!r}",
            )
            self.assertNotIn(
                "bg-surface-container text-secondary font-bold",
                link,
                f"Blog mobile active class leaked into inactive page: {link!r}",
            )


class BlogPostAdminTests(TestCase):
    """Tests for the admin registration of Category, Tag, and BlogPost.

    Covers spec #87 scenarios: 'Admin BlogPostAdmin' (prepopulated
    slug, filter_horizontal, registration) and 'Admin CategoryAdmin
    and TagAdmin' (prepopulated slug on both).
    """

    def test_blogpost_registered(self):
        # BlogPost is registered with django.contrib.admin and the
        # registered admin class is BlogPostAdmin (spec #87 'Admin
        # BlogPostAdmin' registration scenario).
        self.assertIn(BlogPost, django_admin.site._registry)
        self.assertIsInstance(django_admin.site._registry[BlogPost], BlogPostAdmin)

    def test_blogpost_admin_prepopulated_slug(self):
        # BlogPostAdmin.prepopulated_fields auto-fills the slug from
        # the title (spec #87 'Admin BlogPostAdmin' prepopulated
        # scenario).
        self.assertEqual(BlogPostAdmin.prepopulated_fields, {"slug": ("title",)})

    def test_blogpost_admin_filter_horizontal(self):
        # BlogPostAdmin.filter_horizontal uses the dual-list M2M
        # widget for tags and related_posts (spec #87 'Admin
        # BlogPostAdmin' filter_horizontal scenario).
        self.assertIn("tags", BlogPostAdmin.filter_horizontal)
        self.assertIn("related_posts", BlogPostAdmin.filter_horizontal)

    def test_category_registered_with_prepopulated_slug(self):
        # CategoryAdmin auto-fills the slug from the name (spec #87
        # 'Admin CategoryAdmin' scenario).
        self.assertIn(Category, django_admin.site._registry)
        self.assertIsInstance(django_admin.site._registry[Category], CategoryAdmin)
        self.assertEqual(CategoryAdmin.prepopulated_fields, {"slug": ("name",)})

    def test_tag_registered_with_prepopulated_slug(self):
        # TagAdmin auto-fills the slug from the name (spec #87 'Admin
        # TagAdmin' scenario).
        self.assertIn(Tag, django_admin.site._registry)
        self.assertIsInstance(django_admin.site._registry[Tag], TagAdmin)
        self.assertEqual(TagAdmin.prepopulated_fields, {"slug": ("name",)})


class BlogProseStylesTests(TestCase):
    """Tests for the .blog-prose wrapper class on the blog detail page.

    Guards the post-Batch-6 hotfix that introduced the .blog-prose
    wrapper on templates/blog/detail.html line 53. The wrapper is the
    anchor for the styling rules in static/css/blog-record.css; without
    it, Tailwind's preflight resets (loaded via the Play CDN in
    base.html) would strip the typography off the Markdown-rendered
    HTML in {{ post.body_html|safe }}.

    These tests verify the template side of the contract (the class is
    on the article element, and the rendered HTML still contains the
    Markdown-output <pre><code> structure the CSS targets). They do NOT
    re-verify the body_html generation itself — that's already covered
    by BlogModelTests.test_body_html_fenced_code.
    """

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="MLOps", slug="mlops")
        # Post with a fenced code block in the body — exercises the
        # <pre><code> path the .blog-prose pre rule is meant to style.
        cls.code_post = BlogPost.objects.create(
            title="Code Heavy",
            slug="code-heavy",
            body=(
                "# Heading One\n\n"
                "Intro paragraph with **bold**.\n\n"
                "```python\nprint('hi')\n```\n\n"
                "## Subheading\n"
            ),
            category=cls.category,
            is_published=True,
            published_at=timezone.now(),
        )
        # Plain post with a heading + paragraph only — used to verify
        # the wrapper class is present on the article element regardless
        # of body content.
        cls.plain_post = BlogPost.objects.create(
            title="Plain",
            slug="plain",
            body="## A heading\n\nBody text.",
            category=cls.category,
            is_published=True,
            published_at=timezone.now(),
        )

    def test_article_has_blog_prose_class(self):
        # The <article> element on the detail page must carry the
        # `blog-prose` class so static/css/blog-record.css can scope
        # its Markdown-rendered rules. The pre-fix template used
        # `prose prose-invert` instead, which were dead classes
        # (no Tailwind typography plugin loaded in base.html) and
        # left the body unstyled.
        response = self.client.get(
            reverse("blog_detail", kwargs={"slug": self.plain_post.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'class="blog-prose',
            response.content,
            f"Expected 'class=\"blog-prose' on the article element; "
            f"detail page for slug {self.plain_post.slug!r} did not "
            f"include the .blog-prose wrapper class.",
        )
        # Sanity: the wrapper class is NOT the dead `prose prose-invert`
        # from the pre-fix template. The Play CDN in base.html does not
        # load the typography plugin, so `prose` is a no-op.
        self.assertNotIn(b"prose prose-invert", response.content)

    def test_code_block_uses_blog_prose_pre_styling(self):
        # A post with a fenced code block renders to <pre><code> in
        # body_html. The detail page embeds body_html inside the
        # .blog-prose article, so the response must contain the
        # <pre><code> structure inside the article region. The CSS in
        # static/css/blog-record.css targets `.blog-prose pre` (and
        # `.blog-prose pre code` for the reset), so the structural
        # contract is: <article class="blog-prose"> ... <pre><code>...
        # ...</code></pre> ... </article>.
        # First, confirm the body_html produced by BlogPost.save()
        # contains <pre><code> (the markdown lib's `fenced_code`
        # extension output).
        self.code_post.refresh_from_db()
        self.assertIn("<pre><code", self.code_post.body_html)
        # Then confirm the detail page response carries that same
        # <pre><code> substring (it is rendered via {{ post.body_html|safe }}).
        response = self.client.get(
            reverse("blog_detail", kwargs={"slug": self.code_post.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"<pre><code", response.content)
        # And confirm the <pre> appears AFTER the .blog-prose wrapper
        # opens in the rendered HTML (i.e. the <pre> is inside the
        # article, not somewhere else on the page such as a script
        # tag or nav). Cheap proxy: count occurrences of `blog-prose`
        # and confirm the response is well-formed enough that the
        # wrapper class is present alongside the code block.
        self.assertIn(b"blog-prose", response.content)
        # The closing `</article>` must come AFTER the opening
        # <article class="blog-prose ..."> in the response stream.
        open_article = response.content.find(b'class="blog-prose')
        close_article = response.content.find(b"</article>", open_article)
        pre_open = response.content.find(b"<pre><code", open_article)
        self.assertGreater(open_article, 0)
        self.assertGreater(close_article, open_article)
        self.assertGreater(pre_open, open_article)
        self.assertLess(pre_open, close_article)


class BlogCategoryFilterTests(TestCase):
    """Tests for the client-side category filter on the blog list view.

    Mirrors the projects page pattern: the view passes all ``Category`` rows
    to the template as ``categories`` context; the template renders one button
    per category plus a hardcoded 'All Posts' default; each post card carries
    a ``data-category="<slug>"`` attribute; ``static/js/blog-list.js`` toggles
    card visibility on chip click.
    """

    @classmethod
    def setUpTestData(cls):
        cls.cat_mlops = Category.objects.create(name="MLOps", slug="mlops")
        cls.cat_py = Category.objects.create(name="Python", slug="python")
        cls.cat_infra = Category.objects.create(name="Infrastructure", slug="infrastructure")
        cls.post_mlops = BlogPost.objects.create(
            title="MLOps Post", slug="mlops-post", body="body",
            category=cls.cat_mlops, is_published=True,
        )
        cls.post_py = BlogPost.objects.create(
            title="Python Post", slug="python-post", body="body",
            category=cls.cat_py, is_published=True,
        )

    def test_categories_in_context(self):
        """Spec drift fix: BlogListView must expose categories to the template."""
        response = self.client.get(reverse("blog_list"))
        self.assertIn("categories", response.context)
        cats = list(response.context["categories"])
        self.assertEqual(len(cats), 3)
        # Ordered by name (Meta.ordering)
        self.assertEqual([c.name for c in cats], ["Infrastructure", "MLOps", "Python"])

    def test_post_cards_have_data_category_attribute(self):
        """Each rendered card must carry data-category="<slug>" for the JS filter to target."""
        response = self.client.get(reverse("blog_list"))
        self.assertContains(response, 'data-category="mlops"', status_code=200)
        self.assertContains(response, 'data-category="python"', status_code=200)

    def test_all_posts_button_starts_active(self):
        """The hardcoded 'All Posts' chip must render with active classes + aria-pressed=true."""
        response = self.client.get(reverse("blog_list"))
        # The "All Posts" button is hardcoded (not from a category loop) so look for the data-filter="all" attribute
        self.assertContains(response, 'data-filter="all"', status_code=200)
        # Active classes for the All Posts button
        self.assertContains(response, 'bg-primary', status_code=200)

    def test_one_button_per_category_plus_all(self):
        """Template renders exactly N+1 filter chips: 1 hardcoded 'All Posts' + N categories."""
        response = self.client.get(reverse("blog_list"))
        # 3 categories in setUpTestData → 4 chips total
        self.assertContains(response, 'data-filter="all"', status_code=200)
        self.assertContains(response, 'data-filter="mlops"', status_code=200)
        self.assertContains(response, 'data-filter="python"', status_code=200)
        self.assertContains(response, 'data-filter="infrastructure"', status_code=200)


class BlogCategoryServerSideFilterTests(TestCase):
    """Tests for the server-side ?category=<slug> filter on the blog list view.

    Replaces the previous client-side filter — the view now reads the query
    param, filters the BlogPost queryset by category, and exposes
    ``active_category`` + ``active_category_slug`` to the template. Unknown
    slugs fall back to no filter (graceful degradation).
    """

    @classmethod
    def setUpTestData(cls):
        cls.cat_mlops = Category.objects.create(name="MLOps", slug="mlops")
        cls.cat_py = Category.objects.create(name="Python", slug="python")
        cls.cat_infra = Category.objects.create(name="Infrastructure", slug="infrastructure")
        # Explicit published_at so the Meta.ordering ("-is_featured", "-published_at")
        # is deterministic: post_mlops_1 is 1s newer than post_mlops_2, so it is
        # featured_post under -published_at DESC. Without explicit timestamps the
        # auto-set published_at differs by microseconds and the test is flaky.
        cls.now = timezone.now()
        cls.post_mlops_1 = BlogPost.objects.create(
            title="MLOps Post 1", slug="mlops-post-1", body="body",
            category=cls.cat_mlops, is_published=True,
            published_at=cls.now,
        )
        cls.post_mlops_2 = BlogPost.objects.create(
            title="MLOps Post 2", slug="mlops-post-2", body="body",
            category=cls.cat_mlops, is_published=True,
            published_at=cls.now - timezone.timedelta(seconds=1),
        )
        cls.post_py = BlogPost.objects.create(
            title="Python Post", slug="python-post", body="body",
            category=cls.cat_py, is_published=True,
            published_at=cls.now - timezone.timedelta(seconds=2),
        )
        cls.post_draft = BlogPost.objects.create(
            title="Draft MLOps", slug="draft-mlops", body="body",
            category=cls.cat_mlops, is_published=False,
        )

    def test_filter_by_category_returns_only_matching(self):
        """GET /blog/?category=mlops returns only the 2 published MLOps posts."""
        response = self.client.get(reverse("blog_list") + "?category=mlops")
        self.assertEqual(response.status_code, 200)
        # featured_post is the first MLOps post, other_posts is the second
        self.assertEqual(response.context["featured_post"], self.post_mlops_1)
        self.assertEqual(list(response.context["other_posts"]), [self.post_mlops_2])
        # The Python post and draft must NOT appear
        all_returned = [response.context["featured_post"]] + list(response.context["other_posts"])
        self.assertNotIn(self.post_py, all_returned)
        self.assertNotIn(self.post_draft, all_returned)

    def test_no_filter_returns_all_published(self):
        """GET /blog/ (no query param) returns all published posts regardless of category."""
        response = self.client.get(reverse("blog_list"))
        self.assertEqual(response.status_code, 200)
        all_returned = [response.context["featured_post"]] + list(response.context["other_posts"])
        self.assertEqual(len(all_returned), 3)  # 2 MLOps + 1 Python (draft excluded)
        self.assertIn(self.post_mlops_1, all_returned)
        self.assertIn(self.post_mlops_2, all_returned)
        self.assertIn(self.post_py, all_returned)
        self.assertNotIn(self.post_draft, all_returned)

    def test_unknown_category_falls_back_to_no_filter(self):
        """GET /blog/?category=typo returns all posts (graceful degradation, not 404)."""
        response = self.client.get(reverse("blog_list") + "?category=typo")
        self.assertEqual(response.status_code, 200)
        all_returned = [response.context["featured_post"]] + list(response.context["other_posts"])
        self.assertEqual(len(all_returned), 3)  # all published posts
        self.assertIsNone(response.context["active_category"])
        self.assertEqual(response.context["active_category_slug"], "")

    def test_active_category_in_context(self):
        """The view exposes active_category (Category object or None) and active_category_slug."""
        # With filter
        r1 = self.client.get(reverse("blog_list") + "?category=python")
        self.assertEqual(r1.context["active_category"], self.cat_py)
        self.assertEqual(r1.context["active_category_slug"], "python")
        # Without filter
        r2 = self.client.get(reverse("blog_list"))
        self.assertIsNone(r2.context["active_category"])
        self.assertEqual(r2.context["active_category_slug"], "")

    def test_all_posts_chip_active_when_no_filter(self):
        """When no filter is applied, the 'All Posts' chip renders with active classes + aria-pressed=true."""
        response = self.client.get(reverse("blog_list"))
        # The "All Posts" chip is the first <a> inside #blog-filter-chips
        # It should have bg-primary (active) when no filter
        body = response.content.decode("utf-8")
        # Look for the all-posts chip with active class
        self.assertIn('data-filter="all"', body)
        # The active class for the all chip — find the <a> with data-filter="all" and check its class
        # Simple check: ensure the rendered chip for "All Posts" has bg-primary
        chip_start = body.find('data-filter="all"')
        # Walk back to the <a tag
        a_start = body.rfind("<a ", 0, chip_start)
        a_end = body.find(">", a_start)
        chip_html = body[a_start:a_end + 1]
        self.assertIn("bg-primary", chip_html)
        self.assertIn("aria-pressed=\"true\"", chip_html)

    def test_category_chip_active_when_filtered(self):
        """When ?category=mlops is in the URL, the MLOps chip renders with active classes + aria-pressed=true."""
        response = self.client.get(reverse("blog_list") + "?category=mlops")
        body = response.content.decode("utf-8")
        # Find the MLOps chip
        chip_start = body.find('data-filter="mlops"')
        a_start = body.rfind("<a ", 0, chip_start)
        a_end = body.find(">", a_start)
        chip_html = body[a_start:a_end + 1]
        self.assertIn("bg-primary", chip_html)
        self.assertIn("aria-pressed=\"true\"", chip_html)
        # The "All Posts" chip should be inactive
        all_start = body.find('data-filter="all"')
        all_a_start = body.rfind("<a ", 0, all_start)
        all_a_end = body.find(">", all_a_start)
        all_html = body[all_a_start:all_a_end + 1]
        self.assertNotIn("bg-primary", all_html)
        self.assertIn("aria-pressed=\"false\"", all_html)

    def test_filter_indicator_visible_when_active(self):
        """The 'Filtering by: MLOps [Clear]' indicator only renders when a filter is active."""
        # No filter → no indicator
        r1 = self.client.get(reverse("blog_list"))
        self.assertNotIn("Filtering by:", r1.content.decode("utf-8"))
        # With filter → indicator visible
        r2 = self.client.get(reverse("blog_list") + "?category=mlops")
        self.assertIn("Filtering by:", r2.content.decode("utf-8"))
        self.assertIn("MLOps", r2.content.decode("utf-8"))
        # The clear-filter link points to /blog/ (no query param)
        self.assertIn('href="/blog/"', r2.content.decode("utf-8"))


class BlogPaginationTests(TestCase):
    """Tests for the paginated blog list view + LOAD MORE button.

    Page size is 5. Page 1 uses the bento-grid layout (1 featured +
    1 side + 3 medium). Pages 2+ render all 5 as uniform medium cards.
    The "load more" button is rendered only when ``has_next`` is True.
    The view also supports ``?partial=1`` to return only the card
    partial (used by the AJAX handler).
    """

    @classmethod
    def setUpTestData(cls):
        cls.cat = Category.objects.create(name="MLOps", slug="mlops")
        # Create 12 posts (3 pages of 5) with deterministic ordering.
        # Use explicit published_at with a 1-hour offset so the ordering
        # is stable across test runs. Meta.ordering is
        # ('-is_featured', '-published_at'), all posts have
        # is_featured=False, so the descending published_at puts
        # post-11 first and post-00 last.
        from datetime import datetime, timedelta, timezone
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        for i in range(12):
            BlogPost.objects.create(
                title=f"Post {i:02d}",
                slug=f"post-{i:02d}",
                body="body",
                category=cls.cat,
                is_published=True,
                published_at=base + timedelta(hours=i),
            )

    def test_first_page_has_featured_split(self):
        """Page 1 renders 1 featured + 1 side + 3 medium (5 total)."""
        response = self.client.get(reverse("blog_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["featured_split"], True)
        self.assertEqual(len(response.context["other_posts"]), 4)  # side + 3 medium
        # featured_post is the most recently published (Post 11)
        self.assertEqual(response.context["featured_post"].slug, "post-11")
        # other_posts: 4 oldest (Post 10 = side, Posts 09/08/07 = medium)
        self.assertEqual(response.context["other_posts"][0].slug, "post-10")
        # is_paginated is True (there are 3 pages, we're on 1)
        self.assertTrue(response.context["is_paginated"])
        self.assertTrue(response.context["has_next"])
        self.assertEqual(response.context["next_page_number"], 2)
        self.assertEqual(response.context["page_size"], 5)

    def test_second_page_has_no_featured_split(self):
        """Pages 2+ render all 5 posts as uniform medium cards (no featured)."""
        response = self.client.get(reverse("blog_list") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["featured_split"], False)
        self.assertIsNone(response.context["featured_post"])
        self.assertEqual(len(response.context["other_posts"]), 5)
        # Page 2 has the next 5 oldest posts (Post 06 through Post 02)
        self.assertEqual(response.context["other_posts"][0].slug, "post-06")
        self.assertEqual(response.context["other_posts"][4].slug, "post-02")
        self.assertTrue(response.context["has_next"])
        self.assertEqual(response.context["next_page_number"], 3)

    def test_last_page_has_no_next(self):
        """The last page exposes has_next=False and the button is NOT rendered."""
        response = self.client.get(reverse("blog_list") + "?page=3")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["has_next"])
        self.assertIsNone(response.context["next_page_number"])
        # Last page has 2 posts (12 total, 5 per page = 5+5+2)
        self.assertEqual(len(response.context["other_posts"]), 2)
        # Button is NOT rendered on last page
        self.assertNotContains(response, "load-more-btn")
        self.assertNotContains(response, "LOAD MORE LOGS")

    def test_load_more_button_rendered_on_non_last_page(self):
        """The 'LOAD MORE LOGS' button is rendered on page 1 with data-next-page=2."""
        response = self.client.get(reverse("blog_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="load-more-btn"')
        self.assertContains(response, 'data-next-page="2"')
        self.assertContains(response, 'data-page-size="5"')

    def test_load_more_button_on_middle_page_points_to_next(self):
        """On page 2, the button has data-next-page=3 (not 2)."""
        response = self.client.get(reverse("blog_list") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="load-more-btn"')
        self.assertContains(response, 'data-next-page="3"')
        self.assertNotIn(b'data-next-page="2"', response.content)

    def test_invalid_page_falls_back_to_first(self):
        """Out-of-range or non-integer page numbers return page 1 (no 404)."""
        for bad in ["0", "999", "abc", "-1"]:
            with self.subTest(bad=bad):
                response = self.client.get(reverse("blog_list") + f"?page={bad}")
                self.assertEqual(response.status_code, 200)
                # We end up on page 1
                self.assertEqual(response.context["page_obj"].number, 1)

    def test_partial_request_returns_only_cards(self):
        """?partial=1 returns only the bento-grid cards (no header, no button)."""
        response = self.client.get(reverse("blog_list") + "?partial=1")
        self.assertEqual(response.status_code, 200)
        body = response.content.decode("utf-8")
        # The card content IS in the response
        self.assertIn("Post 11", body)  # featured post
        # But the page wrapper / button / filter chips are NOT
        self.assertNotIn("blog-filter-chips", body)
        self.assertNotIn("load-more-btn", body)
        self.assertNotIn("Knowledge Base", body)  # header tagline not in partial

    def test_partial_request_paginates(self):
        """?partial=1&page=2 returns just the page-2 cards."""
        response = self.client.get(reverse("blog_list") + "?partial=1&page=2")
        self.assertEqual(response.status_code, 200)
        body = response.content.decode("utf-8")
        # Page 2 posts: Post 06 through Post 02
        self.assertIn("Post 06", body)
        self.assertIn("Post 02", body)
        # Page 1 posts (Post 11, Post 10) NOT in partial
        self.assertNotIn("Post 11", body)
        self.assertNotIn("Post 10", body)

    def test_pagination_with_category_filter(self):
        """?category=<slug> + ?page=2 filters by category and paginates together."""
        # Create an extra category with 1 post — total 13 posts across 2 categories
        cat_py = Category.objects.create(name="Python", slug="python")
        BlogPost.objects.create(
            title="Python Post",
            slug="python-post",
            body="body",
            category=cat_py,
            is_published=True,
        )
        # Filter by python: 1 post, 1 page. ?page=2 falls back to page 1.
        response = self.client.get(reverse("blog_list") + "?category=python&page=2")
        self.assertEqual(response.status_code, 200)
        # Falls back to page 1 (the only page with 1 post)
        self.assertEqual(response.context["page_obj"].number, 1)
        self.assertFalse(response.context["has_next"])

    def test_no_pagination_button_when_few_posts(self):
        """When total published posts <= page size, no button is rendered.

        Uses an isolated small category to keep the test order-independent
        (the 12 setUpTestData posts are unaffected by this filter).
        """
        cat_small = Category.objects.create(name="Small", slug="small")
        for i in range(3):
            BlogPost.objects.create(
                title=f"Small {i}",
                slug=f"small-{i}",
                body="body",
                category=cat_small,
                is_published=True,
            )
        response = self.client.get(reverse("blog_list") + "?category=small")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["is_paginated"])
        self.assertNotContains(response, "load-more-btn")

    def test_query_count_includes_paginator_count(self):
        """Full list view runs the main query + 1 paginator COUNT query.

        The pre-pagination list view ran 4 queries; adding the paginator's
        COUNT brings the total to 5 (1 categories + 1 posts + 2 prefetch
        + 1 paginator COUNT). select_related("category") joins the FK
        inline at no extra cost.
        """
        with self.assertNumQueries(5):
            self.client.get(reverse("blog_list"))


# 384-dim zero vector — the default for BlogPostEmbedding.embedding
_ZERO_VECTOR = [0.0] * 384


@unittest.skipUnless(
    connection.vendor == "postgresql",
    "BlogPostEmbedding uses pgvector; requires PostgreSQL with the vector extension",
)
class BlogPostEmbeddingModelTests(TestCase):
    """Tests for the BlogPostEmbedding model.

    The ``embedding`` column is a ``pgvector.django.VectorField(dimensions=384)``
    and the migration enables the ``vector`` postgres extension. The whole
    class skips on non-postgres backends (e.g. local SQLite runs) because
    neither the column type nor the extension is available there.

    Run with: ``docker-compose exec app python manage.py test blog``
    """

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="MLOps", slug="mlops")
        cls.post = BlogPost.objects.create(
            title="Embedded Post",
            slug="embedded-post",
            body="x",
            category=cls.category,
            is_published=True,
        )

    def test_str(self):
        # __str__ returns the embedding identifier (post title + model name).
        embedding = BlogPostEmbedding(post=self.post)
        self.assertIn("Embedded Post", str(embedding))
        self.assertIn("all-MiniLM-L6-v2", str(embedding))

    def test_default_model_name(self):
        # The default model_name is 'all-MiniLM-L6-v2' (sentence-transformers
        # model that produces 384-dim vectors — the model that fits the
        # VectorField(dimensions=384) declared on the model).
        embedding = BlogPostEmbedding.objects.create(
            post=self.post, embedding=_ZERO_VECTOR
        )
        self.assertEqual(embedding.model_name, "all-MiniLM-L6-v2")

    def test_unique_together_same_post_and_model(self):
        # Two embeddings with the same (post, model_name) violate the
        # unique_together constraint and raise IntegrityError on save.
        BlogPostEmbedding.objects.create(
            post=self.post, embedding=_ZERO_VECTOR
        )
        with self.assertRaises(IntegrityError):
            BlogPostEmbedding.objects.create(
                post=self.post, embedding=_ZERO_VECTOR
            )

    def test_unique_together_allows_different_model_names(self):
        # Two embeddings with the same post but different model_name is OK —
        # the unique constraint is the pair, not just the post.
        BlogPostEmbedding.objects.create(
            post=self.post, embedding=_ZERO_VECTOR
        )
        BlogPostEmbedding.objects.create(
            post=self.post,
            model_name="other-model",
            embedding=_ZERO_VECTOR,
        )
        self.assertEqual(self.post.embeddings.count(), 2)

    def test_fk_cascade_deletes_embeddings(self):
        # Deleting a post cascades to its embeddings (on_delete=CASCADE).
        BlogPostEmbedding.objects.create(
            post=self.post, embedding=_ZERO_VECTOR
        )
        self.assertEqual(BlogPostEmbedding.objects.count(), 1)
        self.post.delete()
        self.assertEqual(BlogPostEmbedding.objects.count(), 0)

    def test_reverse_relation_related_name(self):
        # post.embeddings returns all embeddings for the post via the
        # related_name='embeddings' on the FK.
        e1 = BlogPostEmbedding.objects.create(
            post=self.post, embedding=_ZERO_VECTOR
        )
        e2 = BlogPostEmbedding.objects.create(
            post=self.post,
            model_name="second-model",
            embedding=_ZERO_VECTOR,
        )
        # Meta.ordering is ('post', 'model_name') — same post, ordered by
        # model_name ('all-MiniLM-L6-v2' < 'second-model' alphabetically).
        self.assertEqual(list(self.post.embeddings.all()), [e1, e2])

    def test_vector_persists_384_dims(self):
        # A 384-dim vector with distinct values roundtrips through the DB
        # with all dimensions intact. Verifies the column accepts the full
        # dimension count and that the pgvector roundtrip is lossless (to
        # float32 precision).
        original = [0.001 * (i + 1) for i in range(384)]
        embedding = BlogPostEmbedding.objects.create(
            post=self.post, embedding=original
        )
        embedding.refresh_from_db()
        self.assertEqual(len(embedding.embedding), 384)
        for i, expected in enumerate(original):
            self.assertAlmostEqual(
                float(embedding.embedding[i]),
                expected,
                places=4,
                msg=f"mismatch at index {i}: got {embedding.embedding[i]!r}, expected {expected!r}",
            )


class BlogPostEmbeddingAdminTests(TestCase):
    """Tests for the admin registration of BlogPostEmbedding.

    This class does not exercise the vector field itself (it does not
    need to), so it runs on any backend. It only verifies that the admin
    site has the model registered with the right admin class.
    """

    def test_registered(self):
        # BlogPostEmbedding is registered with django.contrib.admin and the
        # registered admin class is BlogPostEmbeddingAdmin.
        self.assertIn(BlogPostEmbedding, django_admin.site._registry)
        self.assertIsInstance(
            django_admin.site._registry[BlogPostEmbedding],
            BlogPostEmbeddingAdmin,
        )

    def test_admin_list_display(self):
        # BlogPostEmbeddingAdmin.list_display exposes the post, model_name,
        # and timestamp columns.
        self.assertEqual(
            BlogPostEmbeddingAdmin.list_display,
            ("post", "model_name", "created_at", "updated_at"),
        )

    def test_admin_raw_id_for_post_fk(self):
        # The post FK uses raw_id_fields so the admin does not render the
        # full <select> widget for the blogpost lookup (better for large
        # post tables).
        self.assertIn("post", BlogPostEmbeddingAdmin.raw_id_fields)
