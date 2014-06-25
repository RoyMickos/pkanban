# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PkLog'
        db.create_table(u'pkanban_pklog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pkanban.PkTask'])),
            ('time', self.gf('django.db.models.fields.DateTimeField')()),
            ('event', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'pkanban', ['PkLog'])


    def backwards(self, orm):
        # Deleting model 'PkLog'
        db.delete_table(u'pkanban_pklog')


    models = {
        u'pkanban.pklog': {
            'Meta': {'object_name': 'PkLog'},
            'event': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pkanban.PkTask']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'pkanban.pktask': {
            'Meta': {'object_name': 'PkTask'},
            'completed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'effort': ('django.db.models.fields.IntegerField', [], {}),
            'history': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastmodify': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'valuestream': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pkanban.PkValuestream']", 'null': 'True', 'blank': 'True'})
        },
        u'pkanban.pkvaluestream': {
            'Meta': {'object_name': 'PkValuestream'},
            'phases': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['pkanban.PkWorkPhases']", 'symmetrical': 'False'}),
            'streamname': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'})
        },
        u'pkanban.pkwiptasks': {
            'Meta': {'object_name': 'PkWipTasks'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phase': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pkanban.PkWorkPhases']"}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pkanban.PkTask']"})
        },
        u'pkanban.pkworkphases': {
            'Meta': {'object_name': 'PkWorkPhases'},
            'capacity': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'})
        }
    }

    complete_apps = ['pkanban']