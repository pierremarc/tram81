# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'GeoImage.rotation'
        db.add_column(u'api_geoimage', 'rotation',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'GeoImage.rotation'
        db.delete_column(u'api_geoimage', 'rotation')


    models = {
        u'api.geoimage': {
            'Meta': {'object_name': 'GeoImage'},
            'geom': ('django.contrib.gis.db.models.fields.PolygonField', [], {}),
            'height': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '124'}),
            'pub_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'rotation': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'text': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['api']