from django.core.management.base import BaseCommand

import vinci.search_indexer as si


class Command(BaseCommand):
    help = "Perform a simple search."

    def handle(self, *args, **options):
        results, _, _ = si.search(' '.join(*args))
        for result in results:
            print(result)
