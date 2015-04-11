# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0003_notebook_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='slug',
            field=models.SlugField(default=b'', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='entry',
            name='title',
            field=models.CharField(default=b'', max_length=100, blank=True),
            preserve_default=True,
        ),
    ]
