from django.core.management.base import BaseCommand, CommandError

from vinci.models import Notebook, List, Card, Checklist, ChecklistItem, Label
from django.contrib.auth.models import User

import sqlite3
import datetime
import json

class Command(BaseCommand):
    args = '<json file> <notebook>'
    help = 'Imports a Trello JSON file'

    def handle(self, *args, **options):
        try:
            filename = args[0]
            notebook_slug = args[1]

            with open(filename, 'r') as f:
                data = f.read()

            board = json.loads(data)

            # Get the first user (the admin)
            user = User.objects.all().first()

            # Get the notebook
            nb = Notebook.objects.get(slug=notebook_slug)

            # Flags
            import_lists = True
            import_cards = True
            import_comments = True
            import_checklists = True

            # Label mapping
            print("Importing label mapping")
            label_mapping = {}
            labels = Label.objects.all()
            order = 0
            for trello_mapping in board['labels']:
                label_mapping[trello_mapping['id']] = labels[order]
                order += 1

            # Import the lists
            if import_lists:
                print("Importing lists")
                list_mapping = {}
                for trello_list in board['lists']:
                    if trello_list['closed'] == False:
                        list = List()
                        list.title = trello_list['name']
                        list.notebook = nb
                        list.order = trello_list['pos']
                        list.save()

                        # Map the Trello list ID to our new ID
                        list_mapping[trello_list['id']] = list

            # Import cards
            if import_cards:
                print("Importing cards")
                card_mapping = {}
                for trello_card in board['cards']:
                    if trello_card['closed'] == False and trello_card['idList'] in list_mapping:
                        card_list = list_mapping[trello_card['idList']]

                        card = Card()
                        card.list = card_list
                        card.title = trello_card['name']
                        if trello_card['desc'] != '':
                            card.description = trello_card['desc']
                        card.order = trello_card['pos']
                        card.save()

                        # Add labels
                        for trello_label in trello_card['idLabels']:
                            label = label_mapping[trello_label]
                            card.labels.add(label)

                        card_mapping[trello_card['id']] = card

            # Add comments
            if import_comments:
                print("Importing comments")
                for trello_action in board['actions']:
                    if trello_action['type'] == 'commentCard':
                        card_id = trello_action['data']['card']['id']

                        if card_id in card_mapping:
                            card = card_mapping[card_id]

                            comment = trello_action['data']['text'].strip()

                            # Append the comment to the card's description
                            card.description += "\n\n{}".format(comment)
                            card.description = card.description.strip()
                            card.save()

            # Add checklists
            if import_checklists:
                print("Importing checklists")

                for trello_checklist in board['checklists']:
                    card_id = trello_checklist['idCard']

                    if card_id in card_mapping:
                        card = card_mapping[card_id]

                        # Create and add to card
                        checklist = Checklist()
                        checklist.card = card
                        checklist.title = trello_checklist['name']
                        checklist.order = trello_checklist['pos']
                        checklist.save()

                        # Add items
                        for trello_item in trello_checklist['checkItems']:
                            item = ChecklistItem()
                            item.checklist = checklist
                            item.title = trello_item['name']
                            if trello_item['state'] == 'complete':
                                item.done = True
                            item.order = trello_item['pos']
                            item.save()


            # TODO: Reorder cards to more sane positions

            print("Done! Don't forget to reindex")

        except Exception as e:
            print(e)
