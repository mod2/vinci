# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0014_entry_last_modified'),
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_last_modified', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(max_length=10, choices=[('active', 'active'), ('archived', 'archived'), ('deleted', 'deleted')], default='active')),
                ('title', models.CharField(max_length=255)),
                ('order', models.IntegerField(default=0)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['order', 'title'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Checklist',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_last_modified', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(max_length=10, choices=[('active', 'active'), ('archived', 'archived'), ('deleted', 'deleted')], default='active')),
                ('title', models.CharField(max_length=255)),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['order', 'title'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ChecklistItem',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_last_modified', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(max_length=10, choices=[('active', 'active'), ('archived', 'archived'), ('deleted', 'deleted')], default='active')),
                ('title', models.CharField(max_length=255)),
                ('order', models.IntegerField(default=0)),
                ('done', models.BooleanField(default=False)),
                ('checklist', models.ForeignKey(to='vinci.Checklist', related_name='items')),
            ],
            options={
                'ordering': ['order', 'title'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('title', models.CharField(max_length=255)),
                ('order', models.IntegerField(default=0)),
                ('color', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['order', 'title'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_last_modified', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(max_length=10, choices=[('active', 'active'), ('archived', 'archived'), ('deleted', 'deleted')], default='active')),
                ('title', models.CharField(max_length=255)),
                ('order', models.IntegerField(default=0)),
                ('labels', models.ManyToManyField(blank=True, to='vinci.Label', related_name='labeled_lists')),
            ],
            options={
                'ordering': ['order', 'title'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='card',
            name='checklists',
            field=models.ManyToManyField(blank=True, to='vinci.Checklist', related_name='cards'),
        ),
        migrations.AddField(
            model_name='card',
            name='labels',
            field=models.ManyToManyField(blank=True, to='vinci.Label', related_name='labeled_cards'),
        ),
        migrations.AddField(
            model_name='card',
            name='list',
            field=models.ForeignKey(to='vinci.List', related_name='cards'),
        ),
        migrations.AddField(
            model_name='card',
            name='mentions',
            field=models.ManyToManyField(blank=True, to='vinci.Entry', related_name='mentioned_cards'),
        ),
    ]
