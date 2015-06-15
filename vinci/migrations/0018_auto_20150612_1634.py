# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

default_label_colors = (
    'hsl(2, 58%, 52%)',
    'hsl(32, 60%, 54%)',
    'hsl(78, 54%, 52%)',
    'hsl(157, 87%, 31%)',
    'hsl(198, 62%, 55%)',
    'hsl(207, 67%, 41%)',
    'hsl(280, 34%, 54%)',
    'hsl(319, 58%, 65%)',
)


def create_default_labels(apps, schema_editor):
    Label = apps.get_model('vinci', 'Label')
    for order, color in enumerate(default_label_colors):
        Label.objects.create(order=order, color=color)


def remove_default_labels(apps, schema_editor):
    Label = apps.get_model('vinci', 'Label')
    for order, color in enumerate(default_label_colors):
        Label.objects.filter(order=order, color=color).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0017_auto_20150611_1514'),
    ]

    operations = [
        migrations.AlterField(
            model_name='label',
            name='order',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='label',
            name='title',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.RunPython(create_default_labels, remove_default_labels)
    ]
