# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0015_auto_20150601_1130'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='card',
            name='checklists',
        ),
        migrations.AddField(
            model_name='checklist',
            name='card',
            field=models.ForeignKey(to='vinci.Card', related_name='checklists', default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='list',
            name='notebook',
            field=models.ForeignKey(to='vinci.Notebook', related_name='lists', default=1),
            preserve_default=False,
        ),
    ]
