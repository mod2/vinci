from django.conf.urls import patterns, include, url
from django.contrib import admin
from vinci.views.apis import EntryAPI, CreateEntryAPI


vincipatterns = patterns(
    'vinci.views.web',

    url(r'^$', 'notebooks_list', name='notebooks_list'),
    url(r'^(?P<slug>[^\/]+)/$', 'entries_list', name='notebook'),
    url(r'^(?P<slug>[^\/]+)/add/entry/$', CreateEntryAPI.as_view(),
        name='create_entry'),
    url(r'^(?P<slug>[^\/]+)/entries/$', EntryAPI.as_view(), name='entry'),
)

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),

    url(r'^', include(vincipatterns)),
)
