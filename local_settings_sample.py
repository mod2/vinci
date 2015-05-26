SECRET_KEY = 'vinci'

DEBUG = False

TIME_ZONE = 'America/Denver'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'default.db',
    },
}

# Vinci specific settings
# VINCI_SITE_TITLE = 'Vinci'  # main title for the site
# VINCI_SITE_TITLE_SEP = ' | '  # delimiter to be used in the html titles
# VINCI_DEFAULT_SEARCH_ORDER = '-date'  # default search order
# VINCI_RESULTS_PER_PAGE = 10  # number of results per page

# VINCI_PLUGINS, the plugins to run on each entry before displaying, order
# matters
# VINCI_PLUGINS = [
#     'youtube',
#     'hashtags',
#     'image',
#     'pagelink',
#     'md',
#     'sp',
# ]

# Turns on the non REST apis for simpler integration in other
# applications/programs. Basically adds GET endpoints with query params.
# VINCI_ENABLE_NON_REST_APIS = False
# VINCI_NON_REST_KEY = 'your non-REST API key'

# These should be strings. Used by the quickjump api.
VINCI_DEFAULT_API_KEY_USERNAME = None
VINCI_API_KEY = None
