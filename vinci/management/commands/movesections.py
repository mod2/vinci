from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from vinci.models import Notebook, Entry, Section

class Command(BaseCommand):
    args = '<listfile>'
    help = 'Takes list and updates notebook entries to be in the right sections'

    def handle(self, *args, **options):
        try:
            filename = args[0]
            notebook_slug = filename.replace("output/", "")
            notebook = Notebook.objects.get(slug=notebook_slug)

            with open(filename, 'r') as f:
                lines = f.readlines()

            for line in lines:
                id, section_slug = line.split(':')
                section_slug = section_slug.strip()

                try:
                    section = Section.objects.get(slug=section_slug, notebook=notebook)
                except Exception as e:
                    # Create it
                    section = Section()
                    section.name = section_slug
                    section.slug = section_slug
                    section.notebook = notebook
                    section.save()

                entry = Entry.objects.get(id=id)
                entry.section = section
                entry.save()

            print("Updated {} entries".format(len(lines)))
        except Exception as e:
            print(e)
