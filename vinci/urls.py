from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views.apis import EntryListAPIView, EntryDetailAPIView
from .views.apis import NotebookListAPIView, QuickJumpAPIView
from .views import apis
from rest_framework.routers import DefaultRouter

from vinci.views import apis as vinci_api_views
from vinci.views import web as vinci_web_views

vinciapipatterns = [
    url(r'^$',
        NotebookListAPIView.as_view(),
        name='api_notebook_list'),
    url(r'^quick-jump/$', QuickJumpAPIView.as_view(), name='quick_jump'),
    url(r'^add/$', vinci_api_views.add_payload_endpoint, name='api_add_payload'),
    url(r'^timeline/$', vinci_api_views.update_timeline_day, name='api_update_timeline_day'),
    url(r'^(?P<notebook_slug>[^\/]+)/$',
        EntryListAPIView.as_view(),
        name='api_entry_list'),
    url(r'^(?P<notebook_slug>[^\/]+)/(?P<slug>[^\/]+)/$',
        EntryDetailAPIView.as_view(),
        name='api_entry_detail'),
]

if settings.VINCI_ENABLE_NON_REST_APIS:
    # Prepend the non-REST APIs so they don't get slurped up
    vinciapipatterns = [
        url(r'^(?P<notebook_slug>[^\/]+)/append-today/$',
            vinci_api_views.append_today,
            name='api_entry_append_today'),
        url(r'^add-entry/$',
            vinci_api_views.add_entry,
            name='api_entry_add_entry'),

        # TODO: convert these
        url(r'^(?P<notebook_slug>[^\/]+)/(?P<slug>[^\/]+)/add-revision/$',
            vinci_api_views.add_revision,
            name='api_entry_add_revision'),
        url(r'^(?P<notebook_slug>[^\/]+)/(?P<slug>[^\/]+)/update-revision/(?P<revision_id>[^\/]+)/$',
            vinci_api_views.update_revision,
            name='api_entry_update_revision'),
    ] + vinciapipatterns

vincipatterns = [
    url(r'^$', vinci_web_views.notebooks_list, name='notebooks_list'),
    url(r'^api/', include(vinciapipatterns)),
    url(r'^search/$', vinci_web_views.search_all, name='search_all'),
    url(r'^tag/(?P<tag>[^\/]+)/$', vinci_web_views.search_all_tags, name='search_all_tags'),
    url(r'^meta/timeline/$', vinci_web_views.timeline, name='timeline'),
    url(r'^meta/overview/$', vinci_web_views.overview, name='overview'),
    url(r'^meta/diary/(?P<day>[^\/]+)/$', vinci_web_views.diary_detail, name='diary_detail'),
    url(r'^meta/diary/$', vinci_web_views.diary_home, name='diary_home'),

    url(r'^(?P<notebook_slug>[^\/]+)/$',
        vinci_web_views.notebook_home, name='notebook'),
    url(r'^(?P<notebook_slug>[^\/]+)/settings/$',
        vinci_web_views.notebook_settings, name='notebook_settings'),
    url(r'^(?P<notebook_slug>[^\/]+)/tag/(?P<tag>[^\/]+)/$',
        vinci_web_views.search_notebook_tags, name='search_notebook_tags'),
    url(r'^(?P<notebook_slug>[^\/]+)/search/$',
        vinci_web_views.search_notebook, name='search_notebook'),
    url(r'^(?P<notebook_slug>[^\/]+)/(?P<entry_slug>[^\/]+)/(?P<revision_id>[^\/]+)/$',
        vinci_web_views.revision_detail, name='revision'),
    url(r'^(?P<notebook_slug>[^\/]+)/(?P<entry_slug>[^\/]+)/$',
        vinci_web_views.entry_detail, name='entry'),
]

urlpatterns = [
    url(r'^meta/admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', auth_views.login, name='login'),
    url(r'^accounts/logout/$', auth_views.logout, name='logout'),
    url(r'^accounts/preferences/$', vinci_web_views.prefs_view,
        name='preferences'),
    url(r'^', include(vincipatterns)),
]

urlpatterns += staticfiles_urlpatterns()
