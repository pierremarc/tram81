# Create your views here.

import os

from django.conf import settings
from django.http import HttpResponse, Http404

import mapnik
mapnik.logger.set_severity(mapnik.severity_type.Error)

from .tilenames import tileEdges

import math
def tile_to_longlat(x, y, z):
  n = 2.0 ** z
  lon_deg = x / n * 360.0 - 180.0
  lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
  lat_deg = math.degrees(lat_rad)
  return (lat_deg, lon_deg)

EPSG_3857_proj = mapnik.Projection('+proj=merc +lon_0=0 +k=1 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs')
longlat_proj = mapnik.Projection('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')

class Map(object):
    
    root = os.path.join(settings.MEDIA_ROOT, 'tiles')
    
    def __init__(self):
        print 'CREATE MAP: %s'%(settings.MAPNIK_MAPFILE,)
        self.mapfile = settings.MAPNIK_MAPFILE
        self.map = mapnik.Map(settings.MAPNIK_TILE_SIZE, settings.MAPNIK_TILE_SIZE)
        mapnik.load_map(self.map, self.mapfile)
        #self.map.maximum_extent = mapnik.Box2d(-180,-90,180,90)
        #try:
            #self.map.srs = settings.MAPNIK_MAP_SRS
        #except AttributeError:
            #self.map.srs = EPSG_3857_proj.params()
           
        self.map.zoom_to_box(self.map.maximum_extent)
        
        self.proj = mapnik.Projection(self.map.srs)
        self.transform = mapnik.ProjTransform(longlat_proj, self.proj)
        
        #self.map.zoom_all()
        #self.inverse_transform = mapnik.ProjTransform(self.proj, longlat_proj)
        #mb = self.map.envelope()
        #print 'Map extent: %s; latlon => %s'%(mb, self.inverse_transform.forward(mb))
        
        if not os.path.exists(self.root):
            os.makedirs(self.root)
        
    def get_tile_path(self, z, x, y, image_type='png'):
        sx = str(x)
        sy = str(y)
        sz = str(z)
        tile_dir =  os.path.join(self.root, sz, sx)
        tile_name = '.'.join([sz,sx,sy, image_type])
        tile_path = os.path.join(self.root, tile_name)
        #if not os.path.exists(tile_dir):
            #os.makedirs(tile_dir)
        if not os.path.exists(tile_path):
            im = self.get_tile(z,x,y)
            im.save(tile_path, image_type)
            
        return tile_path
    
    def get_tile(self, z, x, y):
        
        ts = settings.MAPNIK_TILE_SIZE
        self.map.resize(ts, ts)
        
        miny, minx = tile_to_longlat(x ,y ,z)
        maxy, maxx = tile_to_longlat(x + 1, y + 1, z)
        
        bbox = mapnik.Box2d(minx, miny, maxx, maxy)
        map_bbox = self.transform.forward(bbox)
        
        self.map.zoom_to_box(map_bbox)
        if(self.map.buffer_size < (ts/2)):
            self.map.buffer_size = ts / 2
            
        im = mapnik.Image(ts , ts )
        mapnik.render(self.map, im, 1, 0, 0)
        return im

mapnik_map = Map()
def get_tile(request, z,x,y):
    global mapnik_map
    #tile_path = mapnik_map.get_tile_path(int(z),
                                         #int(x),
                                         #int(y))
    #buf = open(tile_path, 'rb').read()
    
    buf = mapnik_map.get_tile(int(z),
                            int(x),
                            int(y)).tostring('png')
    response = HttpResponse()
    response['Content-length'] = len(buf)
    response['Content-Type'] = "image/png"
    response.write(buf)
    return response
