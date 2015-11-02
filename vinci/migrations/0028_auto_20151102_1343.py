# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0027_auto_20151102_1314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notebook',
            name='default_section',
            field=models.ForeignKey(related_name='default_notebooks', null=True, to='vinci.Section', blank=True),
        ),
    ]
