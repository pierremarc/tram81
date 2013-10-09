# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Commenter'
        db.create_table(u'comments_commenter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=128)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'comments', ['Commenter'])

        # Adding model 'Comment'
        db.create_table(u'comments_comment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('commenter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['comments.Commenter'])),
            ('content', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('ts', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('thread', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'comments', ['Comment'])


    def backwards(self, orm):
        # Deleting model 'Commenter'
        db.delete_table(u'comments_commenter')

        # Deleting model 'Comment'
        db.delete_table(u'comments_comment')


    models = {
        u'comments.comment': {
            'Meta': {'object_name': 'Comment'},
            'commenter': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['comments.Commenter']"}),
            'content': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thread': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'ts': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'comments.commenter': {
            'Meta': {'object_name': 'Commenter'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        }
    }

    complete_apps = ['comments']