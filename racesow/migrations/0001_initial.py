# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Tag'
        db.create_table(u'racesow_tag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=15)),
        ))
        db.send_create_signal(u'racesow', ['Tag'])

        # Adding model 'Server'
        db.create_table(u'racesow_server', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['racesow.Player'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('auth_key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('simplified', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('players', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('playtime', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('races', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('last_seen', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal(u'racesow', ['Server'])

        # Adding model 'Map'
        db.create_table(u'racesow_map', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('pk3file', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('levelshotfile', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('races', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('playtime', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('oneliner', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'racesow', ['Map'])

        # Adding M2M table for field tags on 'Map'
        m2m_table_name = db.shorten_name(u'racesow_map_tags')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('map', models.ForeignKey(orm[u'racesow.map'], null=False)),
            ('tag', models.ForeignKey(orm[u'racesow.tag'], null=False))
        ))
        db.create_unique(m2m_table_name, ['map_id', 'tag_id'])

        # Adding model 'MapRating'
        db.create_table(u'racesow_maprating', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['racesow.Player'])),
            ('map', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['racesow.Map'])),
            ('rating', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'racesow', ['MapRating'])

        # Adding unique constraint on 'MapRating', fields ['user', 'map']
        db.create_unique(u'racesow_maprating', ['user_id', 'map_id'])

        # Adding model 'PlayerHistory'
        db.create_table(u'racesow_playerhistory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('simplified', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('playtime', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('races', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('maps', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'racesow', ['PlayerHistory'])

        # Adding model 'Player'
        db.create_table(u'racesow_player', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('admin', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('simplified', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('playtime', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('races', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('maps', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'racesow', ['Player'])

        # Adding model 'RaceHistory'
        db.create_table(u'racesow_racehistory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['racesow.Player'])),
            ('map', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['racesow.Map'])),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['racesow.Server'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('time', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
            ('playtime', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('last_played', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'racesow', ['RaceHistory'])

        # Adding model 'Race'
        db.create_table(u'racesow_race', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['racesow.Player'])),
            ('map', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['racesow.Map'])),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['racesow.Server'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('time', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
            ('playtime', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('last_played', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'racesow', ['Race'])

        # Adding unique constraint on 'Race', fields ['player', 'map']
        db.create_unique(u'racesow_race', ['player_id', 'map_id'])

        # Adding model 'Checkpoint'
        db.create_table(u'racesow_checkpoint', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('race', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['racesow.Race'])),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('time', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'racesow', ['Checkpoint'])

        # Adding unique constraint on 'Checkpoint', fields ['race', 'number']
        db.create_unique(u'racesow_checkpoint', ['race_id', 'number'])


    def backwards(self, orm):
        # Removing unique constraint on 'Checkpoint', fields ['race', 'number']
        db.delete_unique(u'racesow_checkpoint', ['race_id', 'number'])

        # Removing unique constraint on 'Race', fields ['player', 'map']
        db.delete_unique(u'racesow_race', ['player_id', 'map_id'])

        # Removing unique constraint on 'MapRating', fields ['user', 'map']
        db.delete_unique(u'racesow_maprating', ['user_id', 'map_id'])

        # Deleting model 'Tag'
        db.delete_table(u'racesow_tag')

        # Deleting model 'Server'
        db.delete_table(u'racesow_server')

        # Deleting model 'Map'
        db.delete_table(u'racesow_map')

        # Removing M2M table for field tags on 'Map'
        db.delete_table(db.shorten_name(u'racesow_map_tags'))

        # Deleting model 'MapRating'
        db.delete_table(u'racesow_maprating')

        # Deleting model 'PlayerHistory'
        db.delete_table(u'racesow_playerhistory')

        # Deleting model 'Player'
        db.delete_table(u'racesow_player')

        # Deleting model 'RaceHistory'
        db.delete_table(u'racesow_racehistory')

        # Deleting model 'Race'
        db.delete_table(u'racesow_race')

        # Deleting model 'Checkpoint'
        db.delete_table(u'racesow_checkpoint')


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
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'levelshotfile': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'playtime': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
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