# Create your views here.

import json
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
    
    return HttpResponse(json.dumps(ret), content_type="text/plain")



class ImageCreate(CreateView):
    model = GeoImage
    fields = ['image','geom']

class ImageUpdate(UpdateView):
    model = GeoImage
    fields = ['image','geom']

class ImageDelete(DeleteView):
    model = GeoImage
    success_url = reverse_lazy('image')

    
    
    
    
    