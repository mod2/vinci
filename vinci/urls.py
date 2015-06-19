from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from .views.apis import EntryListAPIView, EntryDetailAPIView
from .views.apis import NotebookListAPIView, QuickJumpAPIView
from .views import apis
from rest_framework.routers import DefaultRouter

todo_api_router = DefaultRouter()
todo_api_router.register(r'labels', apis.LabelAPIViewSet)
todo_api_router.register(r'lists', apis.ListAPIViewSet)
todo_api_router.register(r'cards', apis.CardAPIViewSet)
todo_api_router.register(r'checklists', apis.ChecklistAPIViewSet)
todo_api_router.register(r'checklistitems', apis.ChecklistItemAPIViewSet)

vinciapipatterns = [
    url(r'^$',
        NotebookListAPIView.as_view(),
        name='api_notebook_list'),
    url(r'^quick-jump/$', QuickJumpAPIView.as_view(), name='quick_jump'),
    url(r'^(?P<notebook_slug>[^\/]+)/$',
        EntryListAPIView.as_view(),
        name='api_entry_list'),
    url(r'^(?P<notebook_slug>[^\/]+)/(?P<slug>[^\/]+)/$',
        EntryDetailAPIView.as_view(),
        name='api_entry_detail'),
]

if settings.VINCI_ENABLE_NON_REST_APIS:
    # Prepend the non-REST APIs so they don't get slurped up
    vinciapipatterns = patterns(
        '',
        url(r'^(?P<notebook_slug>[^\/]+)/append-today/$',
            'vinci.views.apis.append_today',
            name='api_entry_append_today'),
        url(r'^(?P<notebook_slug>[^\/]+)/add-entry/$',
            'vinci.views.apis.add_entry',
            name='api_entry_add_entry'),
        url(r'^(?P<notebook_slug>[^\/]+)/add-card/$',
            'vinci.views.apis.add_card',
            name='api_entry_add_card'),

        # TODO: convert these
        url(r'^(?P<notebook_slug>[^\/]+)/(?P<slug>[^\/]+)/add-revision/$',
            'vinci.views.apis.add_revision',
            name='api_entry_add_revision'),
        url(r'^(?P<notebook_slug>[^\/]+)/(?P<slug>[^\/]+)/update-revision/(?P<revision_id>[^\/]+)/$',
            'vinci.views.apis.update_revision',
            name='api_entry_update_revision'),
    ) + vinciapipatterns

vincipatterns = patterns(
    'vinci.views.web',

    url(r'^$', 'notebooks_list', name='notebooks_list'),
    url(r'^api/', include(vinciapipatterns)),
    url(r'^api-todo/', include(todo_api_router.urls)),
    url(r'^search/$', 'search_all', name='search_all'),
    url(r'^tag/(?P<tag>[^\/]+)/$', 'search_all_tags', name='search_all_tags'),
    url(r'^today/$', 'today', name='today'),

    url(r'^(?P<notebook_slug>[^\/]+)/$',
        'notebook_home', name='notebook'),
    url(r'^(?P<notebook_slug>[^\/]+)/(?P<section>log|note|page|journal|todo)/$',
        'notebook_section', name='notebook_section'),
    url(r'^(?P<notebook_slug>[^\/]+)/(?P<section>log|note|page|journal|todo)/search/$',
        'search_notebook_section', name='search_notebook_section'),
    url(r'^(?P<notebook_slug>[^\/]+)/tag/(?P<tag>[^\/]+)/$',
        'search_notebook_tags', name='search_notebook_tags'),
    url(r'^(?P<notebook_slug>[^\/]+)/(?P<section>log|note|page|journal|todo)/(?P<entry_slug>[^\/]+)/$',
        'entry_detail', name='entry'),
    url(r'^(?P<notebook_slug>[^\/]+)/(?P<section>log|note|page|journal|todo)/(?P<entry_slug>[^\/]+)/(?P<revision_id>[^\/]+)/$',
        'revision_detail', name='revision'),
    url(r'^(?P<notebook_slug>[^\/]+)/search/$',
        'search_notebook', name='search_notebook'),
    url(r'^(?P<notebook_slug>[^\/]+)/settings/$',
        'notebook_settings', name='notebook_settings'),
)

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', auth_views.login, name='login'),
    url(r'^accounts/logout/$', auth_views.logout, name='logout'),
    url(r'^accounts/preferences/$', 'vinci.views.web.prefs_view',
        name='preferences'),
    url(r'^', include(vincipatterns)),
)
