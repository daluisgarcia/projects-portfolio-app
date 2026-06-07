from django.contrib import admin

from .models import BlogPost, Category, Tag


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "is_published",
        "is_featured",
        "published_at",
        "read_time_minutes",
        "display_order",
    )
    list_filter = ("is_published", "is_featured", "category", "tags")
    search_fields = ("title", "excerpt", "body")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags", "related_posts")
    readonly_fields = (
        "body_html",
        "read_time_minutes",
        "created_at",
        "updated_at",
        "published_at",
    )
    date_hierarchy = "published_at"
    ordering = ("-is_featured", "-published_at")
    list_per_page = 25


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    ordering = ("name",)
