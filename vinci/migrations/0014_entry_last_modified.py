# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0013_auto_20150526_1653'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='last_modified',
            field=models.DateTimeField(null=True, default=None, blank=True),
        ),
    ]
