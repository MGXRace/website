# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('racesow', '0006_historicalplayer_historicalrace'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalrace',
            name='races',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='race',
            name='races',
            field=models.IntegerField(default=0),
        ),
    ]
