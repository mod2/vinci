# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0002_auto_20150317_1724'),
    ]

    operations = [
        migrations.AlterField(
            model_name='revision',
            name='parent',
            field=models.ForeignKey(related_name='children', blank=True, to='vinci.Revision', null=True),
            preserve_default=True,
        ),
    ]
