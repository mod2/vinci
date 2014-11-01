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
    notebook_url = '%s%s' % (url_for('index'), entry.notebook.slug)

    # Prep the HTML
    response = utils.text.process(entry.current_revision.content,
                                  entry,
                                  notebook_url)

    excerpt = entry.excerpt if hasattr(entry, 'excerpt') else ''
    processed_entry = {
        'id': entry.id,
        'notebook': {
            'slug': entry.notebook.slug,
            'name': entry.notebook.name,
        },
        'date': entry.date,
        'content': entry.current_revision.content,
        'title': response['title'],
        'slug': response['slug'],
        'tags': response['tags'],
        'html': Markup(response['content']),
        'plugins': response['plugins'],
        'excerpt': Markup(excerpt),
    }

    return processed_entry
