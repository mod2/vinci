# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0002_auto_20150318_2031'),
    ]

    operations = [
        migrations.AddField(
            model_name='notebook',
            name='status',
            field=models.CharField(default=b'active', max_length=20, choices=[(b'active', b'Active'), (b'archived', b'Archived'), (b'deleted', b'Deleted')]),
            preserve_default=True,
        ),
    ]
