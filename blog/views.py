from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404
from django.views.generic import TemplateView

from .models import BlogPost, Category


# Number of posts per page. Page 1 renders the bento-grid layout
# (1 featured col-span-8 + 1 side col-span-4 + 3 medium col-span-4 = 5).
# Pages 2+ render all 5 as uniform medium cards.
PAGE_SIZE = 5


class BlogListView(TemplateView):
    """Public bento-grid index of published blog posts, with pagination.

    Query params:
      ?category=<slug>  — server-side category filter (graceful fallback to
                          no filter if the slug is unknown).
      ?page=<n>         — 1-indexed page number. Out-of-range or non-integer
                          values fall back to the first page (no 404).
      ?partial=1        — return only the bento-grid cards partial (used by
                          the AJAX "load more" handler in blog-list.js).
                          The partial omits the header, filter chips, and
                          the load-more button — just the cards.

    N+1 protection: a single main SELECT for posts is followed by
    ``select_related`` for the ``category`` FK and ``prefetch_related`` for
    the M2M ``tags`` and self-referential ``related_posts`` relations. The
    paginator adds 1 more COUNT query, bringing the total to 5 queries
    for the full list view and 4 queries for the partial view (no COUNT
    needed since the partial is the next page of a known paginator).
    """

    template_name = "blog/list.html"

    def get_template_names(self):
        if self.request.GET.get("partial"):
            return ["blog/_post_cards.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_page"] = "blog"

        # Server-side category filter via ?category=<slug>. Graceful
        # degradation: unknown slug → no filter applied.
        category_slug = self.request.GET.get("category", "").strip()
        active_category = None
        if category_slug:
            active_category = Category.objects.filter(slug=category_slug).first()

        posts_qs = (
            BlogPost.objects
            .filter(is_published=True)
            .select_related("category")
            .prefetch_related("tags", "related_posts")
        )
        if active_category is not None:
            posts_qs = posts_qs.filter(category=active_category)

        # Paginate. Forgiving on out-of-range / non-integer page numbers:
        # fall back to page 1 instead of raising 404.
        paginator = Paginator(posts_qs, PAGE_SIZE)
        page_number = self.request.GET.get("page", 1)
        try:
            page_obj = paginator.page(page_number)
        except (PageNotAnInteger, EmptyPage):
            page_obj = paginator.page(1)

        # Featured/side split is only on page 1.
        is_first_page = page_obj.number == 1
        page_list = list(page_obj)
        if is_first_page:
            context["featured_post"] = page_list[0] if page_list else None
            context["other_posts"] = page_list[1:]
        else:
            context["featured_post"] = None
            context["other_posts"] = page_list

        context["categories"] = Category.objects.all().order_by("name")
        context["active_category"] = active_category
        context["active_category_slug"] = active_category.slug if active_category else ""

        # Pagination context for template + JS.
        context["page_obj"] = page_obj
        context["paginator"] = paginator
        context["is_paginated"] = page_obj.has_other_pages()
        context["has_next"] = page_obj.has_next()
        context["next_page_number"] = page_obj.next_page_number() if page_obj.has_next() else None
        context["page_size"] = PAGE_SIZE
        context["featured_split"] = is_first_page
        return context


class BlogPostDetailView(TemplateView):
    """Single-column reading page for one published blog post.

    Filters by ``is_published=True`` so a post unpublished between
    list-page load and detail-page click returns 404 (no leaked draft).
    N+1 protection mirrors ``BlogListView`` (category FK + tags and
    related_posts M2M prefetched). ``related_posts`` is additionally
    filtered to published only and capped to 3 (the admin-picked
    related posts, in the order the admin author chose them).
    """

    template_name = "blog/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get("slug")
        try:
            post = (
                BlogPost.objects
                .select_related("category")
                .prefetch_related("tags", "related_posts")
                .get(slug=slug, is_published=True)
            )
        except BlogPost.DoesNotExist:
            raise Http404("Blog post not found")
        context["post"] = post
        context["related_posts"] = list(
            post.related_posts.filter(is_published=True)[:3]
        )
        context["active_page"] = "blog"
        return context
