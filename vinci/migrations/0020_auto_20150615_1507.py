# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('vinci', '0019_auto_20150612_1643'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPrefs',
            fields=[
                ('user', models.OneToOneField(serialize=False, to=settings.AUTH_USER_MODEL, related_name='prefs', primary_key=True)),
            ],
            options={
                'ordering': ['user'],
            },
        ),
        migrations.RenameField(
            model_name='notebook',
            old_name='display_lists',
            new_name='display_todos',
        ),
        migrations.AlterField(
            model_name='entry',
            name='entry_type',
            field=models.CharField(max_length=20, choices=[('log', 'Log'), ('note', 'Note'), ('page', 'Page'), ('journal', 'Journal'), ('todo', 'Todo')], default='log'),
        ),
        migrations.AlterField(
            model_name='notebook',
            name='default_section',
            field=models.CharField(max_length=20, choices=[('log', 'Log'), ('note', 'Note'), ('page', 'Page'), ('journal', 'Journal'), ('todo', 'Todo')], default='log'),
        ),
    ]
