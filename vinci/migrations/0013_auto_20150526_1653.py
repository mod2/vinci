# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0012_auto_20150521_1551'),
    ]

    operations = [
        migrations.AddField(
            model_name='notebook',
            name='condense_notes',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='notebook',
            name='parse_notes',
            field=models.BooleanField(default=False),
        ),
    ]
