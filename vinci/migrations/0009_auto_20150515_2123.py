# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.db.models import Q

def convert_pages(apps, schema_editor):
    Entry = apps.get_model("vinci", "Entry")

    # Iterate through entries with either a title or a slug (pages)
    for entry in Entry.objects.exclude(title='', slug=''):
        entry.entry_type = 'page'
        entry.save()

def convert_pages_reverse(apps, schema_editor):
    Entry = apps.get_model("vinci", "Entry")

    for entry in Entry.objects.filter(entry_type='page'):
        entry.entry_type = 'log'
        entry.save()


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0008_auto_20150515_2047'),
    ]

    operations = [
        migrations.RunPython(convert_pages, convert_pages_reverse),
    ]
