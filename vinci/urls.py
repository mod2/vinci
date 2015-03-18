from django.conf.urls import patterns, include, url
from django.contrib import admin


vincipatterns = patterns(
    'vinci.views.web',

    url(r'^$', 'notebooks_list', name='notebooks_list'),
    url(r'^(?P<notebook_slug>[^\/]+)/$', 'entries_list', name='notebook'),
    url(r'^(?P<notebook_slug>[^\/]+)/(?P<entry_slug>[^\/]+)/$', 'entry_detail',
        name='entry'),
)

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),

    url(r'^', include(vincipatterns)),
)
