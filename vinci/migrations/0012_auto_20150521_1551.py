# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0011_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='status',
            field=models.CharField(default='active', choices=[('active', 'Active'), ('deleted', 'Deleted')], max_length=20),
        ),
        migrations.AlterField(
            model_name='entry',
            name='entry_type',
            field=models.CharField(default='log', choices=[('log', 'Log'), ('note', 'Note'), ('page', 'Page'), ('journal', 'Journal')], max_length=20),
        ),
        migrations.AlterField(
            model_name='entry',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', blank=True, through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='notebook',
            name='group',
            field=models.ForeignKey(to='vinci.Group', blank=True, default=None, related_name='notebooks', null=True),
        ),
    ]
