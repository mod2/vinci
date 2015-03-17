from django.conf import settings


def site_title(request):
    return {
        'SITE_TITLE': settings.SITE_TITLE,
        'SITE_TITLE_SEP': settings.SITE_TITLE_SEP,
    }
