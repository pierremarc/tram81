from django.conf.urls import patterns, url

urlpatterns = patterns('tile.views',
    url(r'^(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+)$', 'get_tile', name='tile'),
)
