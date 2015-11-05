# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0028_auto_20151102_1343'),
    ]

    operations = [
        migrations.RenameField(
            model_name='section',
            old_name='default_view',
            new_name='default_mode',
        ),
        migrations.AddField(
            model_name='notebook',
            name='default_mode',
            field=models.CharField(null=True, blank=True, max_length=30),
        ),
    ]
