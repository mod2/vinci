# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('slug', django_extensions.db.fields.AutoSlugField(editable=False, populate_from=b'title', blank=True, overwrite=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-date'],
                'verbose_name': 'Entry',
                'verbose_name_plural': 'Entries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Notebook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', django_extensions.db.fields.AutoSlugField(editable=False, populate_from=b'name', blank=True, unique=True)),
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
                ('last_modified', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(related_name='revisions', to=settings.AUTH_USER_MODEL)),
                ('entry', models.ForeignKey(related_name='revisions', to='vinci.Entry')),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='vinci.Revision', null=True)),
            ],
            options={
                'ordering': ['-last_modified'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='entry',
            name='notebook',
            field=models.ForeignKey(related_name='entries', to='vinci.Notebook'),
            preserve_default=True,
        ),
    ]
