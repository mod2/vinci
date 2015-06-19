# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0021_list_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='list',
            name='slug',
            field=models.SlugField(blank=True, default=''),
        ),
    ]
