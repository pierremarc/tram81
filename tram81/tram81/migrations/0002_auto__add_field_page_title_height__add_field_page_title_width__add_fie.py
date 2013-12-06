# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Page.title_height'
        db.add_column(u'tram81_page', 'title_height',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Page.title_width'
        db.add_column(u'tram81_page', 'title_width',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Page.title_image'
        db.add_column(u'tram81_page', 'title_image',
                      self.gf('django.db.models.fields.files.ImageField')(default='', max_length=124, blank=True),
                      keep_default=False)

        # Adding field 'Page.content_height'
        db.add_column(u'tram81_page', 'content_height',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Page.content_width'
        db.add_column(u'tram81_page', 'content_width',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Page.content_image'
        db.add_column(u'tram81_page', 'content_image',
                      self.gf('django.db.models.fields.files.ImageField')(default='', max_length=124, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Page.title_height'
        db.delete_column(u'tram81_page', 'title_height')

        # Deleting field 'Page.title_width'
        db.delete_column(u'tram81_page', 'title_width')

        # Deleting field 'Page.title_image'
        db.delete_column(u'tram81_page', 'title_image')

        # Deleting field 'Page.content_height'
        db.delete_column(u'tram81_page', 'content_height')

        # Deleting field 'Page.content_width'
        db.delete_column(u'tram81_page', 'content_width')

        # Deleting field 'Page.content_image'
        db.delete_column(u'tram81_page', 'content_image')


    models = {
        u'tram81.page': {
            'Meta': {'object_name': 'Page'},
            'content': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'content_height': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'content_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '124', 'blank': 'True'}),
            'content_width': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'title_height': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '124', 'blank': 'True'}),
            'title_width': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['tram81']