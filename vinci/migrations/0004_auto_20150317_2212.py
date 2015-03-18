# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0003_auto_20150317_2211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='current_revision',
            field=models.ForeignKey(related_name='entry', default=None, to='vinci.Revision', null=True),
            preserve_default=True,
        ),
    ]
