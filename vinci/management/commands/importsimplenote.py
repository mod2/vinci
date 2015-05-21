from django.core.management.base import BaseCommand, CommandError

from vinci.models import Notebook, Entry, Revision
from django.contrib.auth.models import User

import sqlite3
import datetime
import json

class Command(BaseCommand):
    args = '<json file> <notebook>'
    help = 'Imports an Simplenote JSON file as notes'

    def handle(self, *args, **options):
        try:
            filename = args[0]
            notebook_slug = args[1]

            with open(filename, 'r') as f:
                data = f.read()

            simplenote = json.loads(data)

            # Get the first user (the admin)
            user = User.objects.all().first()

            # Get the notebook
            nb = Notebook.objects.get(slug=notebook_slug)

            # Import the suckers
            for entry in simplenote:
                content = entry['content']
                create_date = entry['createdate']
                last_modified_date = entry['modifydate']

                # Convert to an actual datetime object
                # Format: Jan 07 2011 21:10:26
                created = datetime.datetime.strptime(create_date, "%b %d %Y %H:%M:%S")
                last_modified = datetime.datetime.strptime(last_modified_date, "%b %d %Y %H:%M:%S")

                # Now create the entry and revision
                kwargs = {'content': content,
                          'author': user,
                          'notebook': nb,
                          'entry_type': 'note',
                          'date': created,
                         }

                #print("Fake importing entry {} into notebook {}".format(create_date, nb.name))

                entry = Entry.objects.create(**kwargs)
                entry.save()

                # Update revision last_modified date
                rev = entry.current_revision
                rev.last_modified = last_modified
                rev.save()

                #print("Imported entry {} as {} into notebook {} {}".format(create_date, entry.id, nb.name))
                print("Done! Don't forget to reindex")

        except Exception as e:
            print(e)
