"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from app.robots import robots_txt
from app.sitemaps import sitemap_xml
from blog.views import BlogListView, BlogPostDetailView
from experiences.views import ExperienceListView
from projects.views import LandingView, ProjectsView


urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("robots.txt", robots_txt, name="robots_txt"),
        path("sitemap.xml", sitemap_xml, name="sitemap_xml"),
        path("", LandingView.as_view(), name="landing"),
        path("projects/", ProjectsView.as_view(), name="projects"),
        path("experiences/", ExperienceListView.as_view(), name="experiences"),
        path("blog/", BlogListView.as_view(), name="blog_list"),
        path("blog/<slug:slug>/", BlogPostDetailView.as_view(), name="blog_detail"),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
