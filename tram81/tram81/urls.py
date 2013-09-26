from django.conf.urls import patterns, include, url

from .views import IndexView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})$', IndexView.as_view(), name='archive'),
    url(r'^(?P<pk>\d*)$', IndexView.as_view(), name='index'),
    url(r'^api/', include('api.urls')),
    url(r'^tile/', include('tile.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
