# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-date'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Notebook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.CharField(unique=True, max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Revision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField()),
                ('title', models.TextField()),
                ('slug', models.TextField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(related_name=b'revisions', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(related_name=b'children', to='vinci.Revision', null=True)),
            ],
            options={
                'ordering': ['-date'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='entry',
            name='current_revision',
            field=models.ForeignKey(default=None, to='vinci.Revision', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entry',
            name='notebook',
            field=models.ForeignKey(related_name=b'entries', to='vinci.Notebook'),
            preserve_default=True,
        ),
    ]
