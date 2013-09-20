# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'GeoImage.text'
        db.add_column(u'api_geoimage', 'text',
                      self.gf('django.db.models.fields.TextField')(default=u''),
                      keep_default=False)

        # Adding field 'GeoImage.pub_date'
        db.add_column(u'api_geoimage', 'pub_date',
                      self.gf('django.db.models.fields.DateField')(default=datetime.date.today),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'GeoImage.text'
        db.delete_column(u'api_geoimage', 'text')

        # Deleting field 'GeoImage.pub_date'
        db.delete_column(u'api_geoimage', 'pub_date')


    models = {
        u'api.geoimage': {
            'Meta': {'object_name': 'GeoImage'},
            'geom': ('django.contrib.gis.db.models.fields.PolygonField', [], {}),
            'height': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '124'}),
            'pub_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'text': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'width': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['api']