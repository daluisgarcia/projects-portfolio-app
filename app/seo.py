from django.conf import settings


def site_seo(request):
    return {
        "site_url": settings.SITE_URL,
        "site_name": settings.SITE_NAME,
        "site_author": settings.SITE_AUTHOR,
        "site_default_og_image": settings.SITE_DEFAULT_OG_IMAGE,
        "site_twitter_handle": settings.SITE_TWITTER_HANDLE,
        "og_locale": settings.OG_LOCALE,
        "meta_description_default": settings.META_DESCRIPTION_DEFAULT,
    }
