# Process entries for display

import utils.text
from jinja2 import Markup
from flask import url_for

def process_entries(entries):
    processed_entries = []

    for entry in entries:
        # Prep the HTML
        processed_entries.append(process_entry(entry))

    return processed_entries

def process_entry(entry):
    # Prep the HTML
    html = utils.text.markdownify(entry.content,
                                  url_for('index'),
                                  entry.notebook.slug,
                                  '/tag')

    processed_entry = {
        'id': entry.id,
        'notebook': {
            'slug': entry.notebook.slug,
            'name': entry.notebook.name
            },
        'date': entry.date,
        'content': Markup(html),
    }

    return processed_entry
