# Create your views here.

import json
from django.conf import settings
from django.http import HttpResponse, Http404
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from .models import *


class ImageList(ListView):
    model = GeoImage
    

def image_data(req, pk):
    try:
        im = GeoImage.objects.get(pk=pk)
    except GeoImage.DoesNotExist:
        raise Http404()
    
    ret = {}
    ret['url'] = im.image.url
    ret['height'] = im.height
    ret['width'] = im.width
    ret['geometry'] = json.loads(im.geom.geojson)
    ret['text'] = im.text
    ret['pub_date'] = im.pub_date
    
    return HttpResponse(json.dumps(ret), content_type="text/plain")



class ImageCreate(CreateView):
    model = GeoImage
    fields = ['image','geom', 'pub_date', 'text']
    
    def get_context_data(self, **kwargs):
        context = super(ImageCreate, self).get_context_data(**kwargs)
        context['TILE_SERVER'] = settings.TILE_SERVER
        return context

class ImageUpdate(UpdateView):
    model = GeoImage
    fields = ['image','geom', 'pub_date', 'text']
    
    def get_context_data(self, **kwargs):
        context = super(ImageUpdate, self).get_context_data(**kwargs)
        context['TILE_SERVER'] = settings.TILE_SERVER
        return context

class ImageDelete(DeleteView):
    model = GeoImage
    success_url = reverse_lazy('image')

    
    
    
    
    