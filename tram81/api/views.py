# Create your views here.

import json
from datetime import date
from django.conf import settings
from django.http import HttpResponse, Http404
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from .models import *

from api.models import get_bounds


class ImageList(ListView):
    model = GeoImage
    
    def get_queryset(self):
        return GeoImage.objects.all().order_by('-pub_date')

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

def intersects(A, B):
    return A['minx'] <= B['maxx'] and B['minx'] <= A['maxx'] and A['miny'] <= B['maxy'] and B['miny'] <= A['maxy']

def dbg_intersects(A, B, bid):
    print '[%s]'%bid
    print '%f <= %f = %s'%(A['minx'], B['maxx'], A['minx'] <= B['maxx'])
    print '%f <= %f = %s'%(B['minx'], A['maxx'], B['minx'] <= A['maxx'])
    print '%f <= %f = %s'%(A['miny'], B['maxy'], A['miny'] <= B['maxy'])
    print '%f <= %f = %s'%(B['miny'], A['maxy'], B['miny'] <= A['maxy'])
    print '>> %s'%(intersects(A, B),)
        

def debug_view(req, pk, zoom):
    from tile.models import RiakCache
    c = RiakCache()
    g = GeoImage.objects.get(pk=int(pk))
    base = get_bounds(g.geom)
    ret = []
    for keys in c.bucket.stream_keys():
        for k in keys:
            z, x, y = list(k.split('.'))
            if z == zoom:
                bounds = c.index.get(k).data
                dbg_intersects(base, bounds, k)
                ret.append(dict(key=k,x=x,y=y,z=z,bounds=bounds,damaged=intersects(base, bounds)))
            
    return HttpResponse(json.dumps({'data':ret, 'base':base}), content_type="text/plain")

class ImageCreate(CreateView):
    model = GeoImage
    fields = ['image','geom', 'pub_date', 'text']
    
    def get_context_data(self, **kwargs):
        context = super(ImageCreate, self).get_context_data(**kwargs)
        context['TILE_SERVER'] = settings.TILE_SERVER
        context['TODAY'] = date.today()
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

    
    
    
    
    