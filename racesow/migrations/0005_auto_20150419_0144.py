# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('racesow', '0004_auto_20150408_2340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='name',
            field=models.CharField(null=True, default=None, max_length=64, blank=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='simplified',
            field=models.CharField(null=True, default=None, max_length=64, unique=True, blank=True),
        ),
    ]
