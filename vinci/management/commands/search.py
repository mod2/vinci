from django.core.management.base import BaseCommand

import vinci.search_indexer as si


class Command(BaseCommand):
    help = "Perform a simple search."

    def add_arguments(self, parser):
        parser.add_argument('query', nargs='+', type=str)

    def handle(self, *args, **options):
        query = ' '.join(options['query'])
        results, _, _ = si.search(query)
        for result in results:
            print(result.pk, result.content, result.highlight)
