from django.core.management.base import BaseCommand, CommandError

from vinci.models import Notebook, Entry, Revision
from django.contrib.auth.models import User

import sqlite3
import datetime

class Command(BaseCommand):
    args = '<json file>'
    help = 'Imports an old Vinci SQLite database file'

    def handle(self, *args, **options):
        import_notebooks = True
        import_entries = True

        try:
            filename = args[0]

            conn = sqlite3.connect(filename)

            c = conn.cursor()

            notebooks = {}

            # Get the first user (the admin)
            user = User.objects.all().first()

            for row in c.execute("SELECT * FROM notebook"):
                notebook_id = row[0]
                slug = row[1]
                name = row[2]
                description = row[3] # ignore

                if import_notebooks:
                    nb = Notebook()
                    nb.name = name
                    nb.slug = slug
                    nb.author = user
                    nb.save()

                    print("Imported {}: {}".format(notebook_id, name))
                else:
                    nb = None

                notebooks[notebook_id] = {
                    'name': name,
                    'slug': slug,
                    'object': nb,
                }
            
            # Import entries
            revision_cursor = conn.cursor()

            for row in c.execute("SELECT * FROM entry"):
                entry_id = row[0]
                current_revision_id = int(row[1])
                notebook_id = row[2]
                date = row[3]

                # Get an actual datetime object
                date = datetime.datetime.strptime(date[:19], "%Y-%m-%d %H:%M:%S")

                # Get the revision
                revision_cursor.execute("SELECT * FROM revision WHERE id = ?", (current_revision_id,))
                rev = revision_cursor.fetchone()

                revision_id = rev[0]
                revision_content = rev[1]
                revision_parent_id = rev[2]
                revision_title = rev[3]
                revision_slug = rev[4]
                revision_author_id = rev[5]
                revision_date = rev[6]

                # Prep the content
                tags = ''
                if '----' in revision_content:
                    data = revision_content.split('----')
                    metadata = data[0].strip()
                    content = '----'.join(data[1:]).strip()

                    for line in metadata.split('\n'):
                        linedata = line.split(':')
                        key = linedata[0].strip()
                        value = ':'.join(linedata[1:]).strip()

                        if key == 'tags':
                            # Import tags
                            tags = value
                else:
                    content = revision_content.strip()

                # Get the right notebook
                notebook = Notebook.objects.get(slug=notebooks[notebook_id]['slug'])

                # Now create the entry and revision
                kwargs = {'content': content,
                          'author': user,
                          'notebook': notebook,
                          'date': date,
                         }

                if revision_title:
                    kwargs['title'] = revision_title

                if revision_slug:
                    kwargs['slug'] = revision_slug

                if import_entries:
                    entry = Entry.objects.create(**kwargs)

                    if tags != '':
                        tag_list = [x.strip() for x in tags.split(',')]
                        entry.tags.add(*tag_list)
                        entry.save()

                print("Imported entry {} as {} into notebook {} {}".format(entry_id, entry.id, notebook.name, "- {}".format(tags) if tags else ''))

        except Exception as e:
            print(e)
