# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Checkpoint',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('num', models.IntegerField()),
                ('time', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Gameserver',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('user', models.CharField(max_length=64)),
                ('servername', models.CharField(max_length=255)),
                ('admin', models.CharField(max_length=255)),
                ('playtime', models.BigIntegerField(default=0)),
                ('races', models.PositiveIntegerField(default=0)),
                ('maps', models.IntegerField(default=0)),
                ('created', models.DateTimeField(blank=True, null=True, default=None)),
            ],
        ),
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('longname', models.CharField(max_length=255, blank=True, null=True, default=None)),
                ('file', models.CharField(max_length=255, blank=True, null=True, default=None)),
                ('oneliner', models.CharField(max_length=255, blank=True, null=True, default=None)),
                ('pj_oneliner', models.CharField(max_length=255, blank=True, null=True, default=None)),
                ('freestyle', models.BooleanField(default=False)),
                ('status', models.CharField(max_length=255)),
                ('races', models.IntegerField(default=0)),
                ('playtime', models.BigIntegerField(default=0)),
                ('rating', models.FloatField(blank=True, null=True, default=None)),
                ('ratings', models.IntegerField(default=0)),
                ('downloads', models.IntegerField(default=0)),
                ('force_recompution', models.CharField(max_length=255)),
                ('weapons', models.CharField(max_length=255)),
                ('created', models.DateTimeField(blank=True, null=True, default=None)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('simplified', models.CharField(max_length=64)),
                ('auth_name', models.CharField(max_length=64, blank=True)),
                ('auth_token', models.CharField(max_length=64, blank=True)),
                ('auth_email', models.CharField(max_length=64, blank=True)),
                ('auth_mask', models.CharField(max_length=64, blank=True)),
                ('auth_pass', models.CharField(max_length=64, blank=True)),
                ('session_token', models.CharField(max_length=64, blank=True)),
                ('points', models.IntegerField(default=0)),
                ('races', models.IntegerField(default=0)),
                ('maps', models.IntegerField(default=0)),
                ('diff_points', models.IntegerField(default=0)),
                ('awardval', models.IntegerField(default=0)),
                ('playtime', models.BigIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='PlayerMap',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('time', models.IntegerField(blank=True, null=True, default=None)),
                ('races', models.IntegerField(default=0)),
                ('points', models.IntegerField(default=0)),
                ('playtime', models.BigIntegerField(default=0)),
                ('tries', models.IntegerField(default=0)),
                ('duration', models.BigIntegerField(default=0)),
                ('overall_tries', models.IntegerField(default=0)),
                ('racing_time', models.BigIntegerField(default=0)),
                ('created', models.DateTimeField(blank=True, null=True, default=None)),
                ('prejumped', models.CharField(max_length=64)),
                ('map', models.ForeignKey(to='racesowold.Map', null=True, blank=True, default=None)),
                ('player', models.ForeignKey(to='racesowold.Player', null=True, blank=True, default=None)),
                ('server', models.ForeignKey(to='racesowold.Gameserver', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, default=None)),
            ],
        ),
        migrations.AddField(
            model_name='map',
            name='mapper',
            field=models.ForeignKey(to='racesowold.Player', null=True, blank=True, default=None),
        ),
        migrations.AddField(
            model_name='checkpoint',
            name='map',
            field=models.ForeignKey(to='racesowold.Map', null=True, blank=True, default=None),
        ),
        migrations.AddField(
            model_name='checkpoint',
            name='player',
            field=models.ForeignKey(to='racesowold.Player', null=True, blank=True, default=None),
        ),
    ]
