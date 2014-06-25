# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PkWorkPhases'
        db.create_table(u'pkanban_pkworkphases', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, primary_key=True)),
            ('capacity', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'pkanban', ['PkWorkPhases'])

        # Adding model 'PkValuestream'
        db.create_table(u'pkanban_pkvaluestream', (
            ('streamname', self.gf('django.db.models.fields.CharField')(max_length=50, primary_key=True)),
        ))
        db.send_create_signal(u'pkanban', ['PkValuestream'])

        # Adding M2M table for field phases on 'PkValuestream'
        m2m_table_name = db.shorten_name(u'pkanban_pkvaluestream_phases')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pkvaluestream', models.ForeignKey(orm[u'pkanban.pkvaluestream'], null=False)),
            ('pkworkphases', models.ForeignKey(orm[u'pkanban.pkworkphases'], null=False))
        ))
        db.create_unique(m2m_table_name, ['pkvaluestream_id', 'pkworkphases_id'])

        # Adding model 'PkTask'
        db.create_table(u'pkanban_pktask', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('completed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('history', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('effort', self.gf('django.db.models.fields.IntegerField')()),
            ('lastmodify', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('valuestream', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pkanban.PkValuestream'], null=True, blank=True)),
        ))
        db.send_create_signal(u'pkanban', ['PkTask'])

        # Adding model 'PkWipTasks'
        db.create_table(u'pkanban_pkwiptasks', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('phase', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pkanban.PkWorkPhases'])),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pkanban.PkTask'])),
        ))
        db.send_create_signal(u'pkanban', ['PkWipTasks'])


    def backwards(self, orm):
        # Deleting model 'PkWorkPhases'
        db.delete_table(u'pkanban_pkworkphases')

        # Deleting model 'PkValuestream'
        db.delete_table(u'pkanban_pkvaluestream')

        # Removing M2M table for field phases on 'PkValuestream'
        db.delete_table(db.shorten_name(u'pkanban_pkvaluestream_phases'))

        # Deleting model 'PkTask'
        db.delete_table(u'pkanban_pktask')

        # Deleting model 'PkWipTasks'
        db.delete_table(u'pkanban_pkwiptasks')


    models = {
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