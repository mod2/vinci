from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from vinci.models import Notebook, Entry, Section

class Command(BaseCommand):
    args = ''
    help = 'Outputs map list of all notebooks/sections'

    def handle(self, *args, **options):
        try:
            with open('maplist.txt', 'w') as f:
                for nb in Notebook.objects.all().order_by('slug'):
                    entries = Entry.objects.filter(notebook=nb, section=None).count()
                    if entries > 0:
                        f.write("::{} ({}) -> ::{}\n".format(nb.slug, entries, nb.slug))

                    for section in nb.sections.all().order_by('slug'):
                        entries = Entry.objects.filter(notebook=nb, section=section).count()
                        f.write("::{}/{} ({}) -> ::{}-{}\n".format(nb.slug, section.slug, entries, nb.slug, section.slug))

        except Exception as e:
            print(e)
