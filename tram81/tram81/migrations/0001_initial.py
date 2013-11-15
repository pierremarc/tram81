# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Page'
        db.create_table(u'tram81_page', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('content', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
        ))
        db.send_create_signal(u'tram81', ['Page'])


    def backwards(self, orm):
        # Deleting model 'Page'
        db.delete_table(u'tram81_page')


    models = {
        u'tram81.page': {
            'Meta': {'object_name': 'Page'},
            'content': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['tram81']