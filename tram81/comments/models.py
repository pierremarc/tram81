from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.core.mail import mail_managers
from django.conf import settings


class Comment(models.Model):
    commenter = models.ForeignKey(settings.AUTH_USER_MODEL)
    
    content = models.TextField(default=u'', blank=True)
    ts = models.DateTimeField(auto_now=True)
    
    thread = models.CharField(max_length=256)
    
    def __unicode__(self):
        return (u'%s / %s'%(self.commenter.get_username(),self.thread))
    
    
def notifiy_comment(sender, **kwargs):
    instance = kwargs['instance']
    cname = instance.commenter.get_full_name()
    cid = instance.commenter.get_username()
    message = []
    message.append(u'New comment from: %s <https://www.facebook.com/%s>'%(cname, cid))
    message.append(u'In thread: http://tram81.be/%s'%(instance.thread,))
    message.append(instance.content)
    try:
        mail_managers('New Comment', u'\n\n'.join(message))
    except Exception:
        pass
    
    
post_save.connect(notifiy_comment, sender=Comment)
