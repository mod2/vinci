# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0022_auto_20150619_0903'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='label_cache',
            field=models.CharField(null=True, blank=True, max_length=255),
        ),
    ]
