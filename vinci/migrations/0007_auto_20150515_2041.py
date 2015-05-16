# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0006_entry_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='entry_type',
            field=models.CharField(max_length=20, default='log', choices=[('log', 'Log'), ('note', 'Note'), ('page', 'Page')]),
        ),
        migrations.AddField(
            model_name='notebook',
            name='default_type',
            field=models.CharField(max_length=20, default='log', choices=[('log', 'Log'), ('note', 'Note'), ('page', 'Page')]),
        ),
        migrations.AddField(
            model_name='notebook',
            name='display_logs',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='notebook',
            name='display_notes',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='notebook',
            name='display_pages',
            field=models.BooleanField(default=True),
        ),
    ]
