from django.db import models
from django.contrib.auth import get_user_model

USER_MODEL = get_user_model()


class Comment(models.Model):
    commenter = models.ForeignKey(USER_MODEL)
    
    content = models.TextField(default=u'', blank=True)
    ts = models.DateTimeField(auto_now=True)
    
    thread = models.CharField(max_length=256)
    
