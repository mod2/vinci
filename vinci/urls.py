from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from .views.apis import EntryListAPIView, EntryDetailAPIView
from .views.apis import NotebookListAPIView

vinciapipatterns = patterns(
    '',
    url(r'^$',
        NotebookListAPIView.as_view(),
        name='api_notebook_list'),
    url(r'^(?P<notebook_slug>[^\/]+)/$',
        EntryListAPIView.as_view(),
        name='api_entry_list'),
    url(r'^(?P<notebook_slug>[^\/]+)/(?P<slug>[^\/]+)/$',
        EntryDetailAPIView.as_view(),
        name='api_entry_detail'),
)

vincipatterns = patterns(
    'vinci.views.web',

    url(r'^$', 'notebooks_list', name='notebooks_list'),
    url(r'^api/', include(vinciapipatterns)),
    url(r'^(?P<notebook_slug>[^\/]+)/$', 'entries_list', name='notebook'),
    url(r'^(?P<notebook_slug>[^\/]+)/(?P<entry_slug>[^\/]+)/$', 'entry_detail',
        name='entry'),
)

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', auth_views.login),
    url(r'^accounts/logout/$', auth_views.logout),
    url(r'^', include(vincipatterns)),
)
