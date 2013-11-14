#!/usr/bin/env python
"""
Bulk upload on buratinas

"""



from fractions import Fraction
from exifread import process_file as read_exif
from zipfile import ZipFile
from StringIO import StringIO

from django.core.files.images import ImageFile
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from api.models import GeoImage
from shapely.geometry import MultiPolygon, Polygon, Point

from api.views import login_required
from tile.views import mapnik, Map, EPSG_3857_PROJ, LONGLAT_PROJ


K_Lat = 'GPS GPSLatitude'
K_Lon = 'GPS GPSLongitude'
K_LatRef = 'GPS GPSLatitudeRef'
K_LonRef = 'GPS GPSLongitudeRef'

PX_M = float(0.05)

MAP = Map()


def from_map(pos):
    cc = mapnik.Coord(pos.x, pos.y)
    pcc = MAP.transform.backward(cc)
    return Point(pcc.x, pcc.y)

def to_map(pos):
    cc = mapnik.Coord(pos.x, pos.y)
    pcc = MAP.transform.forward(cc)
    return Point(pcc.x, pcc.y)

def coords(orig_pos):
    return (orig_pos.x, orig_pos.y)

def make_rectangle(img, orig_pos):
    hu = float(img.width) / 2.0 * PX_M
    vu = float(img.height) / 2.0 * PX_M
    
    pos = to_map(orig_pos)
    
    print 'SZ W {}({}) H {}({})'.format(img.width, hu, img.height, vu)
    tl = coords(from_map(Point(pos.x - hu, pos.y + vu)))
    tr = coords(from_map(Point(pos.x + hu, pos.y + vu)))
    bl = coords(from_map(Point(pos.x - hu, pos.y - vu)))
    br = coords(from_map(Point(pos.x + hu, pos.y - vu)))
    
    
    p = Polygon((tl, tr, br, bl, tl))
    print 'w = {}; h = {}'.format(p.bounds[2] - p.bounds[0], p.bounds[3] - p.bounds[1])
    return p


def DMStoDD(d, m , s, ref):
    fd = float(d)
    fm = float(m)
    fs = float(s)
    
    d = fd + (fm / 60.0) + (fs / 3600.0)
    if ref == 'S' or ref == 'W':
        d = d * -1.0
    return d

def RtoNumber(R):
    try:
        return float(Fraction(R.num, R.den))
    except ZeroDivisionError:
        return 0.0
    

def extract_ll(tags):
    xlat = [RtoNumber(x) for x in tags[K_Lat].values]
    xlon = [RtoNumber(x) for x in tags[K_Lon].values]
    
    lat = DMStoDD(xlat[0], xlat[1], xlat[2], tags[K_LatRef].values)
    lon = DMStoDD(xlon[0], xlon[1], xlon[2], tags[K_LonRef].values)
    
    #print '{} {} => {} {}'.format(xlon, xlat, lon, lat)
    return Point(lon, lat)

def main():
    import sys
    zfn = sys.argv[1]
    process_zip(zfn)
    
def process_zip(zfn):
    
    z = ZipFile(zfn)
    infos = z.infolist()
    
    ids = []
    
    for info in infos:
        f = StringIO()
        f.write(z.read(info))
        f.seek(0)
        ll = extract_ll(read_exif(f))
        f.seek(0)
        img = ImageFile(f)
        item = GeoImage()
        bbox = make_rectangle(img, ll)
        item.geom = bbox.wkt
        item.width = img.width
        item.height = img.height
        try:
            item.image.save(info.filename, img)
            ids.append(item.id)
        except Exception, e:
            print str(e)
        
        print u'{}: {}'.format(info.filename, ll)
        f.close()
        
    return ids
        
@login_required
def view(request):
    if request.method == 'POST':
        fs = request.FILES
        
        f = fs['zip']
        process_zip(f)
        return redirect('/')
    else:
        ctx = RequestContext(request)
        #print ctx
        return render_to_response('bulk.html',
                          {},
                          context_instance=ctx)

 
if __name__ == "__main__":
    main()
            

        
