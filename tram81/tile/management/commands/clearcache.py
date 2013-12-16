
import os

from django.db import connection
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from tile.models import MongoCache

class Command(BaseCommand):
    help = 'Clear tile server cache'

    def handle(self, *args, **options):
        cache = MongoCache()
        
        for item in cache.index.find():
            path = item['path']
            id = item['_id']
            if id is not None:
                try:
                    cache.index.remove(id)
                    os.unlink(path)
                except Exception, e:
                    self.stdout.write('[clearcache] Failed to delete %s, %s'%(id, path))
                    print str(e)