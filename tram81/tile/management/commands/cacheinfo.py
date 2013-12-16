
import os

from django.db import connection
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from api.models import MongoCache

class Command(BaseCommand):
    help = 'Few informations about cache state'

    def handle(self, *args, **options):
        cache = MongoCache()
        
        self.stdout.write('There are %d entries in the index' % cache.index.find().count())
        