# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def create_default_list(apps, schema_editor):
    List = apps.get_model('vinci', 'List')
    Notebook = apps.get_model('vinci', 'Notebook')
    for notebook in Notebook.objects.all():
        List.objects.create(
            title='Default',
            order=-1,
            notebook=notebook,
        )


def remove_default_lists(apps, schema_editor):
    List = apps.get_model('vinci', 'List')
    List.objects.filter(title='Default', order=-1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0018_auto_20150612_1634'),
    ]

    operations = [
        migrations.RunPython(create_default_list, remove_default_lists)
    ]
