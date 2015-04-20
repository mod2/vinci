# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
        ('vinci', '0005_auto_20150417_1150'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', verbose_name='Tags', through='taggit.TaggedItem', to='taggit.Tag'),
        ),
    ]
