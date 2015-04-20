from django.core.management.base import BaseCommand

import vinci.search_indexer as si


class Command(BaseCommand):
    help = "Create search index of entries in database."

    def handle(self, *args, **options):
        si.get_or_create_index()
