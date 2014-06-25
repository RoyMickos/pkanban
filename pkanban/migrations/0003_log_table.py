# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName". 
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.

    def backwards(self, orm):
        "Write your backwards methods here."

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
    symmetrical = True
