# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0025_entry_section'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='custom_css',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='section',
            name='dotfile',
            field=models.TextField(null=True, blank=True),
        ),
    ]
