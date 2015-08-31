# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'Map', fields ['name']
        db.create_unique(u'racesow_map', ['name'])


    def backwards(self, orm):
        # Removing unique constraint on 'Map', fields ['name']
        db.delete_unique(u'racesow_map', ['name'])


    models = {
        u'racesow.checkpoint': {
            'Meta': {'unique_together': "(('race', 'number'),)", 'object_name': 'Checkpoint'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'race': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['racesow.Race']"}),
            'time': ('django.db.models.fields.IntegerField', [], {})
        },
        u'racesow.map': {
            'Meta': {'object_name': 'Map'},
            'compute_points': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_computation': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'levelshotfile': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'oneliner': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'pk3file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'playtime': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'races': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['racesow.Tag']", 'symmetrical': 'False'})
        },
        u'racesow.maprating': {
            'Meta': {'unique_together': "(('user', 'map'),)", 'object_name': 'MapRating'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'map': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['racesow.Map']"}),
            'rating': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['racesow.Player']"})
        },
        u'racesow.player': {
            'Meta': {'object_name': 'Player'},
            'admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maps': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'maps_finished': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'playtime': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'points': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'races': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'simplified': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        u'racesow.playerhistory': {
            'Meta': {'object_name': 'PlayerHistory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maps': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'playtime': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'races': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'simplified': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'racesow.race': {
            'Meta': {'unique_together': "(('player', 'map'),)", 'object_name': 'Race'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_played': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'map': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['racesow.Map']"}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['racesow.Player']"}),
            'playtime': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'points': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rank': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['racesow.Server']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'time': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        },
        u'racesow.racehistory': {
            'Meta': {'object_name': 'RaceHistory'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_played': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'map': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['racesow.Map']"}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['racesow.Player']"}),
            'playtime': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'points': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rank': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['racesow.Server']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'time': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        },
        u'racesow.server': {
            'Meta': {'object_name': 'Server'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'auth_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'players': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'playtime': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'races': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'simplified': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['racesow.Player']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        u'racesow.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        }
    }

    complete_apps = ['racesow']