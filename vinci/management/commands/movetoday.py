from django.core.management.base import BaseCommand, CommandError

from vinci.models import Notebook, List, Card
from django.contrib.auth.models import User

import sqlite3
import datetime
import json

class Command(BaseCommand):
    help = 'For each Today list, moves all items to the corresponding Inbox list'

    def handle(self, *args, **options):
        try:
            today_lists = List.objects.filter(slug='today')

            for list in today_lists:
                try:
                    inbox_list = List.objects.get(slug='inbox', notebook=list.notebook)

                    num_cards = inbox_list.get_active_cards().count()
                    if num_cards > 0:
                        # Reorder existing cards so the new ones show up in order
                        # (If there's just one, order=0 will put it at the top)
                        list_cards = Card.objects.filter(list=inbox_list).order_by('order')
                        for card in list_cards:
                            card.order += num_cards
                            card.save()

                    # Move all cards from list to inbox_list
                    order = 0
                    for card in list.get_active_cards():
                        card.list = inbox_list
                        card.order = order
                        card.save()

                        order += 1
                except Exception as e:
                    pass

            print("Done! Don't forget to reindex")

        except Exception as e:
            print(e)
