from django.conf.urls import patterns, include, url

from .views import IndexView, JSConf

from django.contrib import admin

urlpatterns = patterns('',
    url(r'^(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})$', IndexView.as_view(), name='archive'),
    url(r'^(?P<pk>\d*)$', IndexView.as_view(), name='index'),
    url(r'^js/$', JSConf.as_view(), name='js_conf'),
    url(r'^api/', include('api.urls')),
    url(r'^tile/', include('tile.urls')),
    url(r'^comments/', include('comments.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^social/', include('social.apps.django_app.urls', namespace='social')),
    url(r'^bulk/$','tram81.bulk.view'),
)

admin.autodiscover()
