# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0023_card_label_cache'),
    ]

    operations = [
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, default='')),
                ('status', models.CharField(max_length=20, default='active', choices=[('active', 'Active'), ('archived', 'Archived'), ('deleted', 'Deleted')])),
                ('default_view', models.CharField(null=True, blank=True, max_length=30)),
                ('dotfile', models.TextField()),
                ('custom_css', models.TextField()),
            ],
        ),
        migrations.RemoveField(
            model_name='card',
            name='labels',
        ),
        migrations.RemoveField(
            model_name='card',
            name='list',
        ),
        migrations.RemoveField(
            model_name='card',
            name='mentions',
        ),
        migrations.RemoveField(
            model_name='checklist',
            name='card',
        ),
        migrations.RemoveField(
            model_name='checklistitem',
            name='checklist',
        ),
        migrations.RemoveField(
            model_name='list',
            name='labels',
        ),
        migrations.RemoveField(
            model_name='list',
            name='notebook',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='entry_type',
        ),
        migrations.RemoveField(
            model_name='notebook',
            name='condense_notes',
        ),
        migrations.RemoveField(
            model_name='notebook',
            name='display_journals',
        ),
        migrations.RemoveField(
            model_name='notebook',
            name='display_logs',
        ),
        migrations.RemoveField(
            model_name='notebook',
            name='display_notes',
        ),
        migrations.RemoveField(
            model_name='notebook',
            name='display_pages',
        ),
        migrations.RemoveField(
            model_name='notebook',
            name='display_todos',
        ),
        migrations.RemoveField(
            model_name='notebook',
            name='parse_notes',
        ),
        migrations.AlterField(
            model_name='notebook',
            name='default_section',
            field=models.CharField(null=True, blank=True, max_length=20),
        ),
        migrations.DeleteModel(
            name='Card',
        ),
        migrations.DeleteModel(
            name='Checklist',
        ),
        migrations.DeleteModel(
            name='ChecklistItem',
        ),
        migrations.DeleteModel(
            name='Label',
        ),
        migrations.DeleteModel(
            name='List',
        ),
        migrations.AddField(
            model_name='section',
            name='notebook',
            field=models.ForeignKey(related_name='sections', to='vinci.Notebook'),
        ),
    ]
