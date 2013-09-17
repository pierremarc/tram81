from django.contrib.gis import admin
from .models import *

class GeoImageAdmin(admin.OSMGeoAdmin):
    pass


admin.site.register(GeoImage, GeoImageAdmin)