import re

from django.core.management.base import BaseCommand

from vinci.models import Entry
from vinci.utils import get_or_create_notebook, get_or_create_section


class Command(BaseCommand):
    args = ''
    help = 'Flattens notebook sections based on map list'

    def handle(self, *args, **options):
        try:
            with open('maplist.txt', 'r') as f:
                for line in f.readlines():
                    print('\n---\n{}'.format(line))
                    # ::my-notebook-slug/log (40) -> ::foo #wiki
                    m = re.match("::(?P<srcnotebook>[a-z-]+)(/(?P<srcsection>[a-z-]+))? \(\d+\) -> ::(?P<dstnotebook>[a-z-]+)( #(?P<tag>[a-z-]+))?", line.strip())
                    if m:
                        source_notebook = m.group('srcnotebook')
                        source_section = m.group('srcsection')
                        dest_notebook = m.group('dstnotebook')
                        dest_tag = m.group('tag')
                    else:
                        source_notebook = None
                        source_section = None
                        dest_notebook = None
                        dest_tag = None

                    # Get the destination notebook
                    dest_nb = get_or_create_notebook(dest_notebook)

                    # Get the source notebook/section
                    src_nb = get_or_create_notebook(source_notebook)
                    if source_section is not None:
                        src_sect = get_or_create_section(source_section,
                                                         source_notebook)
                    else:
                        src_sect = None

                    # Go through all source entries and change
                    # notebook/section fields and add tag
                    if src_sect is not None:
                        entries = Entry.objects.filter(notebook=src_nb,
                                                       section=src_sect)
                    else:
                        entries = dest_nb.entries.all()

                    for index, entry in enumerate(entries):
                        entry.notebook = dest_nb
                        entry.section = None
                        entry.save()

                        if dest_tag:
                            entry.tags.add(dest_tag.strip())
                            entry.save()

        except Exception as e:
            print(e)
