from django.contrib.gis.db import models
from django.core.urlresolvers import reverse

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
    
    
    text = models.TextField(default=u'')
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
        