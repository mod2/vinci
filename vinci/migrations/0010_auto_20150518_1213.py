# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0009_auto_20150515_2123'),
    ]

    operations = [
        migrations.AddField(
            model_name='notebook',
            name='display_journals',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='notebook',
            name='default_section',
            field=models.CharField(default='log', max_length=20, choices=[('log', 'Log'), ('note', 'Note'), ('page', 'Page'), ('journal', 'Journal')]),
        ),
    ]
