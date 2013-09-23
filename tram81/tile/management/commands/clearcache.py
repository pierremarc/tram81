
from django.db import connection
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import riak

class Command(BaseCommand):
    help = 'Clear tile server cache'

    def handle(self, *args, **options):
        RC = settings.RIAK_TILE_CONNECTION
        self.client = riak.RiakClient(**RC)
        self.bucket = self.client.bucket(settings.RIAK_TILE_BUCKET)
        self.index = self.client.bucket(settings.RIAK_TILE_BUCKET + '_index')
        
        for R in self.index.stream_keys():
            for r in R:
                self.bucket.delete(r)
                self.index.delete(r)