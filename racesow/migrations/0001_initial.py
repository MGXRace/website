# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Checkpoint',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('time', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('pk3file', models.FileField(blank=True, upload_to='maps')),
                ('levelshotfile', models.FileField(blank=True, upload_to='levelshots')),
                ('enabled', models.BooleanField(default=True)),
                ('races', models.IntegerField(default=0)),
                ('playtime', models.BigIntegerField(default=0)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('oneliner', models.CharField(max_length=255, blank=True)),
                ('compute_points', models.BooleanField(default=False)),
                ('last_computation', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='MapRating',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('rating', models.IntegerField()),
                ('map', models.ForeignKey(to='racesow.Map')),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('username', models.CharField(max_length=64, unique=True)),
                ('admin', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=64)),
                ('simplified', models.CharField(max_length=64, unique=True)),
                ('playtime', models.BigIntegerField(default=0)),
                ('races', models.IntegerField(default=0)),
                ('maps', models.IntegerField(default=0)),
                ('maps_finished', models.IntegerField(default=0)),
                ('points', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='PlayerHistory',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('username', models.CharField(max_length=64)),
                ('name', models.CharField(max_length=64)),
                ('simplified', models.CharField(max_length=64, unique=True)),
                ('playtime', models.BigIntegerField(default=0)),
                ('races', models.IntegerField(default=0)),
                ('maps', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Race',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('time', models.IntegerField(blank=True, null=True, default=None)),
                ('playtime', models.BigIntegerField(default=0)),
                ('points', models.IntegerField(default=0)),
                ('rank', models.IntegerField(default=0)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_played', models.DateTimeField(default=django.utils.timezone.now)),
                ('map', models.ForeignKey(to='racesow.Map')),
                ('player', models.ForeignKey(to='racesow.Player')),
            ],
        ),
        migrations.CreateModel(
            name='RaceHistory',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('time', models.IntegerField(blank=True, null=True, default=None)),
                ('playtime', models.BigIntegerField(default=0)),
                ('points', models.IntegerField(default=0)),
                ('rank', models.IntegerField(default=0)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_played', models.DateTimeField(default=django.utils.timezone.now)),
                ('map', models.ForeignKey(to='racesow.Map')),
                ('player', models.ForeignKey(to='racesow.Player')),
            ],
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('auth_key', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('simplified', models.CharField(max_length=255)),
                ('players', models.TextField(blank=True)),
                ('playtime', models.BigIntegerField(default=0)),
                ('races', models.PositiveIntegerField(default=0)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_seen', models.DateTimeField(blank=True, null=True, default=None)),
                ('user', models.ForeignKey(to='racesow.Player', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, default=None)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=15)),
            ],
        ),
        migrations.AddField(
            model_name='racehistory',
            name='server',
            field=models.ForeignKey(to='racesow.Server', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, default=None),
        ),
        migrations.AddField(
            model_name='race',
            name='server',
            field=models.ForeignKey(to='racesow.Server', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, default=None),
        ),
        migrations.AddField(
            model_name='maprating',
            name='user',
            field=models.ForeignKey(to='racesow.Player'),
        ),
        migrations.AddField(
            model_name='map',
            name='tags',
            field=models.ManyToManyField(to='racesow.Tag'),
        ),
        migrations.AddField(
            model_name='checkpoint',
            name='race',
            field=models.ForeignKey(to='racesow.Race'),
        ),
        migrations.AlterUniqueTogether(
            name='race',
            unique_together=set([('player', 'map')]),
        ),
        migrations.AlterUniqueTogether(
            name='maprating',
            unique_together=set([('user', 'map')]),
        ),
        migrations.AlterUniqueTogether(
            name='checkpoint',
            unique_together=set([('race', 'number')]),
        ),
    ]
