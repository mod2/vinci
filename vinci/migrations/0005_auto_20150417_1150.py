# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('vinci', '0004_auto_20150408_1843'),
    ]

    operations = [
        migrations.AddField(
            model_name='notebook',
            name='author',
            field=models.ForeignKey(related_name='notebooks', to=settings.AUTH_USER_MODEL, default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='entry',
            name='slug',
            field=models.SlugField(default='', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='entry',
            name='title',
            field=models.CharField(max_length=100, default='', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='notebook',
            name='slug',
            field=django_extensions.db.fields.AutoSlugField(editable=False, blank=True, unique=True, populate_from='name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='notebook',
            name='status',
            field=models.CharField(max_length=20, choices=[('active', 'Active'), ('archived', 'Archived'), ('deleted', 'Deleted')], default='active'),
            preserve_default=True,
        ),
    ]
