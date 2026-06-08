import math

import markdown
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from pgvector.django import VectorField


class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    excerpt = models.TextField(blank=True, default="")
    body = models.TextField()
    body_html = models.TextField(blank=True, default="", editable=False)
    cover_image_url = models.URLField(max_length=500, blank=True, default="")
    cover_image_alt = models.CharField(max_length=200, blank=True, default="")
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="posts",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="posts",
        blank=True,
    )
    related_posts = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="related_to",
        blank=True,
    )
    is_published = models.BooleanField(default=False, db_index=True)
    is_featured = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    read_time_minutes = models.PositiveIntegerField(default=1, editable=False)
    priority = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
    )
    display_order = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-is_featured", "-published_at")
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        word_count = len((self.body or "").split())
        self.read_time_minutes = max(1, math.ceil(word_count / 200))

        self.body_html = markdown.markdown(
            self.body or "",
            extensions=["fenced_code", "tables", "nl2br"],
        )

        prior_published = (
            BlogPost.objects.filter(pk=self.pk)
            .values_list("is_published", flat=True)
            .first()
        )
        if (
            self.is_published
            and self.published_at is None
            and (prior_published is False or prior_published is None)
        ):
            self.published_at = timezone.now()

        super().save(*args, **kwargs)


class BlogPostEmbedding(models.Model):
    """Vector embedding of a blog post for semantic search / similarity.

    Stores a fixed-dimension vector (384 — sized for the sentence-transformers
    ``all-MiniLM-L6-v2`` model or compatible 384-dim embedders) keyed by
    the embedding model name. The ``(post, model_name)`` unique constraint
    allows storing embeddings from multiple models side-by-side, so swapping
    the embedding provider later does not lose prior vectors.

    Requires the ``pgvector`` PostgreSQL extension. The extension is enabled
    by the initial migration of this model via ``VectorExtension()``.
    """

    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name="embeddings",
    )
    embedding = VectorField(dimensions=384)
    model_name = models.CharField(max_length=100, default="all-MiniLM-L6-v2")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("post", "model_name")]
        ordering = ("post", "model_name")
        verbose_name = "Blog Post Embedding"
        verbose_name_plural = "Blog Post Embeddings"

    def __str__(self):
        return f"Embedding for {self.post.title} ({self.model_name})"
