# Create your views here.

import json
from datetime import date
from django.conf import settings
from django.http import HttpResponse, Http404
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.utils.encoding import force_str
from django.shortcuts import resolve_url
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth import REDIRECT_FIELD_NAME
try:
    from urllib.parse import urlparse
except ImportError:     # Python 2
    from urlparse import urlparse
    
from functools import wraps

from .models import *

from api.models import get_bounds


def login_required(view):
    @wraps(view)
    def _wrapped_view(request, *args, **kwargs):
        u = request.user
        if u.is_authenticated() and u.is_staff:
            return view(request, *args, **kwargs)
        path = request.build_absolute_uri()
        
        resolved_login_url = force_str( resolve_url('/api/login/'))
        login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
        current_scheme, current_netloc = urlparse(path)[:2]
        if ((not login_scheme or login_scheme == current_scheme) and
            (not login_netloc or login_netloc == current_netloc)):
            path = request.get_full_path()
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(
            path, resolved_login_url, REDIRECT_FIELD_NAME)
    return _wrapped_view

class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls):
        return login_required(super(LoginRequiredMixin, cls).as_view())


class ImageList(LoginRequiredMixin, ListView):
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
    from tile.models import MongoCache
    c = MongoCache()
    g = GeoImage.objects.get(pk=int(pk))
    base = get_bounds(g.geom)
    polygon = c.get_polygon(base)
    request = { 'center' : { '$geoIntersects' : { '$geometry' : polygon } } }
        
    ret = []
    for item in c.index.find(request):
        k = item['_id']
        z, x, y = list(k.split('_'))
        #if z == zoom:
        bounds = item['bounds']
        ret.append(c.get_polygon(bounds))
    centers = []
    for item in c.index.find():
        centers.append(item['center'])
        
    return HttpResponse(json.dumps({'data':ret, 'base':base, 'centers':centers}), content_type="text/plain")


class ImageCreate(LoginRequiredMixin, CreateView):
    model = GeoImage
    fields = ['image','geom', 'pub_date', 'text']
    
    def get_context_data(self, **kwargs):
        context = super(ImageCreate, self).get_context_data(**kwargs)
        context['TILE_SERVER'] = settings.TILE_SERVER
        context['TODAY'] = date.today()
        return context


class ImageUpdate(LoginRequiredMixin, UpdateView):
    model = GeoImage
    fields = ['image','geom', 'pub_date', 'text']
    
    def get_context_data(self, **kwargs):
        context = super(ImageUpdate, self).get_context_data(**kwargs)
        context['TILE_SERVER'] = settings.TILE_SERVER
        return context


class ImageDelete(LoginRequiredMixin, DeleteView):
    model = GeoImage
    success_url = reverse_lazy('image')

    
    
    
    
    