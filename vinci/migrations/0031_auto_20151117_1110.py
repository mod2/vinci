# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0030_auto_20151117_1059'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='section',
            name='custom_css',
        ),
        migrations.RemoveField(
            model_name='section',
            name='dotfile',
        ),
    ]
