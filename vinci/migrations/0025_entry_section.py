# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0024_auto_20151029_1536'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='section',
            field=models.ForeignKey(to='vinci.Section', null=True, blank=True, related_name='entries'),
        ),
    ]
