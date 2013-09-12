from django.conf.urls import patterns, include, url

from .views import IndexView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^tile/', include('tile.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
