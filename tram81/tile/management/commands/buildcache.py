
import os

from django.db import connection
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from optparse import make_option

from api.models import GeoImage, get_bounds
from tile.models import MongoCache
from tile.views import map_pool
from tile.tilenames import tileXY


class Command(BaseCommand):
    help = 'Seeds cache'
    
    option_list = BaseCommand.option_list + (
        make_option('--min',
            dest='min_zoom',
            type="int",
            default=10,
            help='Minimum zoom'),
        make_option('--max',
            dest='max_zoom',
            type="int",
            default=18,
            help='Maximum zoom'),
        )

    def handle(self, *args, **options):
        global map_pool
        images = GeoImage.objects.all()
        
        min_zoom = options['min_zoom']
        max_zoom = options['max_zoom'] + 1
        
        for image in images:
            self.stdout.write('[buildcache] image %d from zoom %d to %d\n'
                                % (image.pk, min_zoom, max_zoom - 1))
            try:
                bounds = get_bounds(image.geom)
                for z in range(min_zoom, max_zoom):
                    minx, maxy = tileXY(bounds['miny'], 
                                    bounds['minx'], z)
                    
                    maxx, miny = tileXY(bounds['maxy'], 
                                    bounds['maxx'], z)
                    
                    # we buffer the cache a bit
                    for x in range(minx -1, maxx +1):
                        for y in range(miny -1, maxy +1):
                            map_pool.get_map().get_tile(z,x,y)
            except Exception, e:
                print 'failed: %s'%(e,)
        