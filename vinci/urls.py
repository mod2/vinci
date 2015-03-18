from django.conf.urls import patterns, include, url
from django.contrib import admin
# from rest_framework import routers
# from .views.apis import NotebookViewSet, EntryViewSet, EntryListAPIView
from .views.apis import EntryListAPIView, EntryDetailAPIView
from .views.apis import NotebookListAPIView

# router = routers.SimpleRouter()
# router.register(r'notebook', NotebookViewSet)
# router.register(r'entry', EntryViewSet)

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
    # url(r'^api/', include(router.urls)),
    url(r'^api/', include(vinciapipatterns)),
    url(r'^(?P<notebook_slug>[^\/]+)/$', 'entries_list', name='notebook'),
    url(r'^(?P<notebook_slug>[^\/]+)/(?P<entry_slug>[^\/]+)/$', 'entry_detail',
        name='entry'),
)

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),

    url(r'^', include(vincipatterns)),
)
