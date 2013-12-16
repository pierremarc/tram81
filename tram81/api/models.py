from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_save, post_save

from tile.models import MongoCache

from datetime import date

class GeoImage(models.Model):
    
    height = models.IntegerField(default=0, editable=False)
    width = models.IntegerField(default=0, editable=False)
    image = models.ImageField(upload_to='images', 
                              height_field='height', 
                              width_field='width', 
                              max_length=124)
    geom = models.PolygonField(srid=4326)
    objects = models.GeoManager()
    
    
    text = models.TextField(default=u'', blank=True)
    pub_date = models.DateField(default=date.today)

    def __str__(self): 
        return self.image.url
    
    def get_absolute_url(self):
        return reverse('image_update', kwargs={'pk': self.pk})

    @property
    def img_thumbnail(self):
        from easy_thumbnails.files import get_thumbnailer
        options = {'size': (360 /2, 240 /2), 'crop': True}
        return get_thumbnailer(self.image).get_thumbnail(options).url
        
    @property
    def img_large(self):
        from easy_thumbnails.files import get_thumbnailer
        options = {'size': (360 *3, 240 *3), 'crop': 'smart'}
        return get_thumbnailer(self.image).get_thumbnail(options).url
        
        
        
        
        
def get_bounds(poly):
    x_pts = [t[0] for t in poly.envelope.coords[0]]
    y_pts = [t[1] for t in poly.envelope.coords[0]]
    minx = reduce(lambda a,b: min(a,b), x_pts)
    maxx = reduce(lambda a,b: max(a,b), x_pts)
    miny = reduce(lambda a,b: min(a,b), y_pts)
    maxy = reduce(lambda a,b: max(a,b), y_pts)
    return dict(minx=minx,miny=miny, maxx=maxx, maxy=maxy)
        
def invalidate_current(sender, **kwargs):
    c = MongoCache()
    instance = kwargs['instance']
    if instance.id:
        obj = GeoImage.objects.get(pk=instance.id)
        c.DELETE(get_bounds(obj.geom))
        
def invalidate_new(sender, **kwargs):
    c = MongoCache()
    instance = kwargs['instance']
    c.DELETE(get_bounds(instance.geom))
    
pre_save.connect(invalidate_current, sender=GeoImage, weak=False, dispatch_uid='tram81.geoimage.ic')
post_save.connect(invalidate_new, sender=GeoImage, weak=False, dispatch_uid='tram81.geoimage.in')
        
        