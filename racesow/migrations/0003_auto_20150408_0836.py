# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('racesow', '0002_auto_20150408_0744'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkpoint',
            name='race',
            field=models.ForeignKey(related_name='checkpoints', to='racesow.Race'),
        ),
    ]
