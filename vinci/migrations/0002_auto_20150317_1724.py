# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notebook',
            name='description',
        ),
        migrations.AlterField(
            model_name='notebook',
            name='slug',
            field=django_extensions.db.fields.AutoSlugField(editable=False, populate_from=b'name', blank=True, unique=True),
        ),
    ]
