# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0016_auto_20150602_2058'),
    ]

    operations = [
        migrations.AddField(
            model_name='notebook',
            name='display_lists',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='entry',
            name='entry_type',
            field=models.CharField(default='log', choices=[('log', 'Log'), ('note', 'Note'), ('page', 'Page'), ('journal', 'Journal'), ('list', 'List')], max_length=20),
        ),
        migrations.AlterField(
            model_name='notebook',
            name='default_section',
            field=models.CharField(default='log', choices=[('log', 'Log'), ('note', 'Note'), ('page', 'Page'), ('journal', 'Journal'), ('list', 'List')], max_length=20),
        ),
    ]
