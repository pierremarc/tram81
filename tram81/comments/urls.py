from django.conf.urls import patterns, include, url

from .views import ThreadView

urlpatterns = patterns('',
    url(r'new$', 'comments.views.create_comment', name='comment_new'),
    url(r'(?P<thread>[\d-]+)$', ThreadView.as_view(), name='comments'),
)
