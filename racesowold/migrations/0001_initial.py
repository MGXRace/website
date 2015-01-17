# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Player'
        db.create_table(u'racesowold_player', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('simplified', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('auth_name', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('auth_token', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('auth_email', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('auth_mask', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('auth_pass', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('session_token', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('points', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('races', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('maps', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('diff_points', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('awardval', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('playtime', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
        ))
        db.send_create_signal(u'racesowold', ['Player'])

        # Adding model 'Map'
        db.create_table(u'racesowold_map', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('longname', self.gf('django.db.models.fields.CharField')(default=None, max_length=255, null=True, blank=True)),
            ('file', self.gf('django.db.models.fields.CharField')(default=None, max_length=255, null=True, blank=True)),
            ('oneliner', self.gf('django.db.models.fields.CharField')(default=None, max_length=255, null=True, blank=True)),
            ('pj_oneliner', self.gf('django.db.models.fields.CharField')(default=None, max_length=255, null=True, blank=True)),
            ('mapper', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['racesowold.Player'], null=True, blank=True)),
            ('freestyle', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('races', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('playtime', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('rating', self.gf('django.db.models.fields.FloatField')(default=None, null=True, blank=True)),
            ('ratings', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('downloads', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('force_recompution', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('weapons', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal(u'racesowold', ['Map'])

        # Adding model 'Gameserver'
        db.create_table(u'racesowold_gameserver', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('servername', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('admin', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('playtime', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('races', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('maps', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal(u'racesowold', ['Gameserver'])

        # Adding model 'Checkpoint'
        db.create_table(u'racesowold_checkpoint', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['racesowold.Player'], null=True, blank=True)),
            ('map', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['racesowold.Map'], null=True, blank=True)),
            ('num', self.gf('django.db.models.fields.IntegerField')()),
            ('time', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'racesowold', ['Checkpoint'])

        # Adding model 'PlayerMap'
        db.create_table(u'racesowold_playermap', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['racesowold.Player'], null=True, blank=True)),
            ('map', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['racesowold.Map'], null=True, blank=True)),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['racesowold.Gameserver'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('time', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
            ('races', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('points', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('playtime', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('tries', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('duration', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('overall_tries', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('racing_time', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
            ('prejumped', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal(u'racesowold', ['PlayerMap'])


    def backwards(self, orm):
        # Deleting model 'Player'
        db.delete_table(u'racesowold_player')

        # Deleting model 'Map'
        db.delete_table(u'racesowold_map')

        # Deleting model 'Gameserver'
        db.delete_table(u'racesowold_gameserver')

        # Deleting model 'Checkpoint'
        db.delete_table(u'racesowold_checkpoint')

        # Deleting model 'PlayerMap'
        db.delete_table(u'racesowold_playermap')


    models = {
        u'racesowold.checkpoint': {
            'Meta': {'object_name': 'Checkpoint'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'map': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['racesowold.Map']", 'null': 'True', 'blank': 'True'}),
            'num': ('django.db.models.fields.IntegerField', [], {}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['racesowold.Player']", 'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.IntegerField', [], {})
        },
        u'racesowold.gameserver': {
            'Meta': {'object_name': 'Gameserver'},
            'admin': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maps': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'playtime': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'races': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'servername': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'racesowold.map': {
            'Meta': {'object_name': 'Map'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'downloads': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'file': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'force_recompution': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'freestyle': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'longname': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'mapper': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['racesowold.Player']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'oneliner': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'pj_oneliner': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'playtime': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'races': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rating': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'ratings': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'weapons': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'racesowold.player': {
            'Meta': {'object_name': 'Player'},
            'auth_email': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'auth_mask': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'auth_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'auth_pass': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'auth_token': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'awardval': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'diff_points': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maps': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'playtime': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'points': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'races': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'session_token': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'simplified': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'racesowold.playermap': {
            'Meta': {'object_name': 'PlayerMap'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'map': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['racesowold.Map']", 'null': 'True', 'blank': 'True'}),
            'overall_tries': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['racesowold.Player']", 'null': 'True', 'blank': 'True'}),
            'playtime': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'points': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'prejumped': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'races': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'racing_time': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['racesowold.Gameserver']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'time': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'tries': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['racesowold']