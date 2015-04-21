# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('racesow', '0005_auto_20150419_0144'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalPlayer',
            fields=[
                ('id', models.IntegerField(db_index=True, verbose_name='ID', blank=True, auto_created=True)),
                ('username', models.CharField(db_index=True, max_length=64)),
                ('admin', models.BooleanField(default=False)),
                ('name', models.CharField(null=True, blank=True, max_length=64, default=None)),
                ('simplified', models.CharField(null=True, db_index=True, blank=True, max_length=64, default=None)),
                ('playtime', models.BigIntegerField(default=0)),
                ('races', models.IntegerField(default=0)),
                ('maps', models.IntegerField(default=0)),
                ('maps_finished', models.IntegerField(default=0)),
                ('points', models.IntegerField(default=0)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='+', on_delete=django.db.models.deletion.SET_NULL)),
            ],
            options={
                'verbose_name': 'historical player',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='HistoricalRace',
            fields=[
                ('id', models.IntegerField(db_index=True, verbose_name='ID', blank=True, auto_created=True)),
                ('time', models.IntegerField(null=True, blank=True, default=None)),
                ('playtime', models.BigIntegerField(default=0)),
                ('points', models.IntegerField(default=0)),
                ('rank', models.IntegerField(default=0)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_played', models.DateTimeField(default=django.utils.timezone.now)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='+', on_delete=django.db.models.deletion.SET_NULL)),
                ('map', models.ForeignKey(null=True, to='racesow.Map', related_name='+', db_constraint=False, blank=True)),
                ('player', models.ForeignKey(null=True, to='racesow.Player', related_name='+', db_constraint=False, blank=True)),
                ('server', models.ForeignKey(null=True, to='racesow.Server', related_name='+', db_constraint=False, blank=True)),
            ],
            options={
                'verbose_name': 'historical race',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
    ]
