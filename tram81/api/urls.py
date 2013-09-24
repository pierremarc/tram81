from django.conf.urls import patterns, url
from .views import ImageList, ImageCreate, ImageUpdate, ImageDelete

urlpatterns = patterns('api.views',
    url(r'image/debug/(?P<pk>\d+)/(?P<zoom>\d+)$', 'debug_view'),
    url(r'image/data/(?P<pk>\d+)$', 'image_data', name='image_data'),
    url(r'image$', ImageList.as_view(), name='image'),
    url(r'image/add/$', ImageCreate.as_view(), name='image_add'),
    url(r'image/(?P<pk>\d+)/$', ImageUpdate.as_view(), name='image_update'),
    url(r'image/(?P<pk>\d+)/delete/$', ImageDelete.as_view(), name='image_delete'),
)
