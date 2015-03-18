# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0004_auto_20150317_2212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='current_revision',
            field=models.ForeignKey(related_name='entry', to='vinci.Revision'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='revision',
            name='slug',
            field=models.CharField(max_length=100),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='revision',
            name='title',
            field=models.CharField(max_length=100),
            preserve_default=True,
        ),
    ]
