# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinci', '0007_auto_20150515_2041'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notebook',
            old_name='default_type',
            new_name='default_section',
        ),
    ]
