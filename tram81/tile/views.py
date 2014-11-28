# Create your views here.

import os
import math
from collections import namedtuple

from django.conf import settings
from django.http import HttpResponse, Http404
from django.contrib.gis.geos import Polygon, MultiPolygon

from .models import RiakCache, MongoCache


import mapnik
mapnik.logger.set_severity(mapnik.severity_type.Error)

from .tilenames import tileEdges

import math
from threading import Lock

from api.models import GeoImage
from PIL import Image
from StringIO import StringIO

def tile_to_longlat(x, y, z):
  n = 2.0 ** z
  lon_deg = x / n * 360.0 - 180.0
  lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
  lat_deg = math.degrees(lat_rad)
  return (lat_deg, lon_deg)

EPSG_3857_PROJ = mapnik.Projection('+proj=merc +lon_0=0 +k=1 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs')
LONGLAT_PROJ = mapnik.Projection('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')

IntBox = namedtuple('Box',('minx','miny','maxx','maxy'), verbose=False)

def box_is_valid(ib):
    return ib.maxx > ib.minx and ib.maxy > ib.miny

def box_to_poly(box):
    bl = (box.minx,box.miny)
    tl = (box.minx,box.maxy)
    tr = (box.maxx,box.maxy)
    br = (box.maxx,box.miny)
    return Polygon((bl,tl,tr,br,bl))

def poly_to_box(poly):
    x_pts = [t[0] for t in poly.envelope.coords[0]]
    y_pts = [t[1] for t in poly.envelope.coords[0]]
    minx = reduce(lambda a,b: min(a,b), x_pts)
    maxx = reduce(lambda a,b: max(a,b), x_pts)
    miny = reduce(lambda a,b: min(a,b), y_pts)
    maxy = reduce(lambda a,b: max(a,b), y_pts)
    return mapnik.Box2d(minx,miny,maxx,maxy)

def round_box(box):
    return IntBox(*map(int,map(round, box)))

class ImageMixer(object):
    def __init__(self):
        pass
    
    
    def op_multiply(self, base, top, base_box, top_box):
        if not box_is_valid(base_box) or not box_is_valid(top_box):
            return
        bpix = base.load()
        
        
        byy = range(base_box.maxy -1, base_box.miny -1, -1)
        bxx = range(base_box.minx, base_box.maxx)
        
        sz = (base_box.maxx - base_box.minx, 
              base_box.maxy - base_box.miny)
        
        quad = ( top_box.minx, top_box.maxy - 1, # tl
                top_box.minx, top_box.miny ,  # bl
                top_box.maxx, top_box.miny ,  # br
                top_box.maxx, top_box.maxy - 1)  # tr
        
        #t_tmp = top.transform(sz, Image.QUAD, quad, Image.BICUBIC)
        #tpix = t_tmp.load()
        #t_tmp.save('debug.png')
        #tpix = top.transform(sz, Image.QUAD, quad, Image.BICUBIC).load()
        
        cropped_im = top.transform( (top_box.maxx - top_box.minx,
                                     top_box.maxy - top_box.miny),
                                    Image.EXTENT, (top_box.minx, top_box.maxy - 1,
                                                   top_box.maxx, top_box.miny)
                                    )
        tpix = cropped_im.resize(sz, Image.ANTIALIAS).load()
        
        
        for y_idx in xrange(len(byy)):
            by = byy[y_idx]
            for x_idx in xrange(len(bxx)):
                bx = bxx[x_idx]
                vb = bpix[bx,by]
                vt = tpix[x_idx, y_idx]
                #v =  tuple(map(lambda a,b: a*b/255, vb, vt))
                v = [0,0,0,255]
                for cc in range(3):
                    v[cc] = vb[cc] * vt[cc] / 255
                bpix[bx,by] = tuple(v)
                
    def _ts(self, a, min_, max_, T):
        r = a - min_
        return r * float(T) / (max_ - min_)
    
        
    def mix(self, tile, bbox):
        wkt = box_to_poly(bbox.forward(LONGLAT_PROJ)).wkt
        geo_images = GeoImage.objects.filter(geom__bboverlaps=wkt)
        
        
        if geo_images:
            src_image = Image.open(StringIO(tile.tostring('png')))
            #base = Image.new(src_image.mode, src_image.size, "white")
        
            for geo_image in geo_images:
                box = poly_to_box(geo_image.geom)
                ibox = box.intersect(bbox)
                if not ibox.valid():
                    continue
                
                try:
                    im = Image.open(geo_image.image.path)
                except Exception:
                    pass

                if geo_image.rotation > 0:
                    rgba_im = im.convert('RGBA')
                    # rotated_im = rgba_im.rotate(geo_image.rotation, filter=Image.BICUBIC, expand=True)
                    rotated_im = rgba_im.rotate(geo_image.rotation, expand=True)
                    im = Image.new("RGBA", rotated_im.size, "white")
                    im.paste(rotated_im, (0,0), rotated_im)
                
                # project intersection on image
                ox = self._ts(ibox.minx, box.minx, box.maxx, im.size[0])
                oy = self._ts(ibox.maxy, box.maxy, box.miny, im.size[1])
                dx = self._ts(ibox.maxx, box.minx, box.maxx, im.size[0])
                dy = self._ts(ibox.miny, box.maxy, box.miny, im.size[1])
                O = round_box(mapnik.Box2d(ox,oy,dx,dy))
                
                # project intersection on tile
                b_ox = self._ts(ibox.minx, bbox.minx, bbox.maxx, src_image.size[0])
                b_oy = self._ts(ibox.maxy, bbox.maxy, bbox.miny, src_image.size[1])
                b_dx = self._ts(ibox.maxx, bbox.minx, bbox.maxx, src_image.size[0])
                b_dy = self._ts(ibox.miny, bbox.maxy, bbox.miny, src_image.size[1])
                B = round_box(mapnik.Box2d(b_ox, b_oy, b_dx, b_dy))
                

                self.op_multiply(src_image, im, B, O)
                
            #AB = round_box(mapnik.Box2d(0,0,base.size[0],base.size[1]))
            #self.op_multiply(base, src_image, AB, AB)
            
            f = StringIO()
            #base.transpose(Image.FLIP_TOP_BOTTOM).save(f, 'PNG')
            src_image.save(f, 'PNG')
            return mapnik.Image.fromstring(f.getvalue())
                
        return tile
       
class PILDatasource(mapnik.PythonDatasource):
    def __init__(self, image, geom):
        self.image = image
        self.geom = poly_to_box(geom)
        super(PILDatasource, self).__init__()

    def features(self, query):
        bbox = query.bbox
        ibox = self.geom.intersect(bbox)
        if not ibox.valid():
            raise Exception('Invalid intersection')
        

        

class Map(object):
    
    root = os.path.join(settings.MEDIA_ROOT, 'tiles')
    cache = MongoCache()
    
    def __init__(self):
        print 'CREATE MAP: %s'%(settings.MAPNIK_MAPFILE,)
        
        self.mutex = Lock()
        
        self.mapfile = settings.MAPNIK_MAPFILE
        self.map = mapnik.Map(settings.MAPNIK_TILE_SIZE, settings.MAPNIK_TILE_SIZE)
        mapnik.load_map(self.map, self.mapfile)
        
        # self.map.zoom_to_box(self.map.maximum_extent)

        self.proj = mapnik.Projection(self.map.srs)
        self.transform = mapnik.ProjTransform(LONGLAT_PROJ, self.proj)
        self.inverse_transform = mapnik.ProjTransform(self.proj, LONGLAT_PROJ)

            
    
    def get_tile(self, z, x, y):
        sx = str(x)
        sy = str(y)
        sz = str(z)
        cname = '.'.join([sz,sx,sy])
        if self.cache.HAS(cname):
            return self.cache.GET(cname)
        
        miny, minx = tile_to_longlat(x ,y ,z)
        maxy, maxx = tile_to_longlat(x + 1, y + 1, z)
        bounds_tms = dict(miny=miny, minx=minx, maxy=maxy, maxx=maxx)
        bounds = dict(miny=maxy, minx=minx, maxy=miny, maxx=maxx)
        tile = self._get_tile(z,x,y, bounds_tms).tostring('png')
        self.cache.PUT(cname, bounds, tile)
        return tile
    
    def _get_tile(self, z, x, y, bounds):
        self.mutex.acquire()
        try:
            ts = settings.MAPNIK_TILE_SIZE
            self.map.resize(ts, ts)
            
            bbox = mapnik.Box2d(bounds['minx'], 
                                bounds['miny'], 
                                bounds['maxx'], 
                                bounds['maxy'])
            map_bbox = self.transform.forward(bbox)
            
            self.map.zoom_to_box(map_bbox)
            if(self.map.buffer_size < (ts/2)):
                self.map.buffer_size = ts / 2
                
            im = mapnik.Image(ts , ts )
            mapnik.render(self.map, im, 1, 0, 0)
        except Exception:
            pass
        finally:
            self.mutex.release()

        return ImageMixer().mix(im, bbox)


class MapPool(object):
    def __init__(self, pool_max=6):
        self.pool_max = pool_max
        self.current_idx = 0
        self.maps = []
        for i in range(self.pool_max):
            self.maps.append(Map())
        
    def get_map(self):
        self.current_idx += 1
        if self.current_idx >= self.pool_max:
            self.current_idx = 0
            
        return self.maps[self.current_idx]

map_pool = MapPool()

def get_tile(request, z,x,y):
    global map_pool
    
    buf = map_pool.get_map().get_tile(int(z),
                            int(x),
                            int(y))
    response = HttpResponse()
    response['Content-length'] = len(buf)
    response['Content-Type'] = "image/png"
    response.write(buf)
    return response
