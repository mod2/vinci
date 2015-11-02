# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0026_auto_20151029_1547'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notebook',
            name='author',
        ),
        migrations.RemoveField(
            model_name='revision',
            name='author',
        ),
    ]
