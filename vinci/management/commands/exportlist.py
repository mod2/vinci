from django.core.management.base import BaseCommand, CommandError

from vinci.models import Notebook, Entry
from django.contrib.auth.models import User

import sqlite3
import datetime
import json

class Command(BaseCommand):
    args = '<json file> <notebook>'
    help = 'Exports entry IDs sorted by entry type'

    def handle(self, *args, **options):
        try:
            notebooks = Notebook.objects.all()

            for notebook in notebooks:
                data = ''

                # Go through each entry and map to type
                for entry in Entry.objects.filter(notebook__slug=notebook.slug):
                    data += '{}:{}\n'.format(entry.id, entry.entry_type)

                with open('output/{}'.format(notebook.slug), 'w') as f:
                    f.write(data)
        except Exception as e:
            print(e)
