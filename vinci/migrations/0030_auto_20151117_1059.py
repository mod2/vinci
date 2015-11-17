# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0029_auto_20151105_1554'),
    ]

    operations = [
        migrations.AddField(
            model_name='notebook',
            name='custom_css',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='notebook',
            name='dotfile',
            field=models.TextField(null=True, blank=True),
        ),
    ]
