from django.conf.urls import patterns, include, url
from django.contrib import admin

vincipatterns = patterns(
    'vinci.views.web',

    url(r'^$', 'notebooks_list', name='notebooks_list'),
    url(r'^(?P<slug>[^\/]+)/$', 'notebook_detail', name='notebook'),
)

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),

    url(r'^', include(vincipatterns)),
)
