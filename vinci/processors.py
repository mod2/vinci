from django.conf import settings


def site_title(request):
    return {
        'SITE_TITLE': settings.VINCI_SITE_TITLE,
        'SITE_TITLE_SEP': settings.VINCI_SITE_TITLE_SEP,
    }


def api_key(request):
    return {
        'API_KEY': settings.VINCI_API_KEY,
    }
