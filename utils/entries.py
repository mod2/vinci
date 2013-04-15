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
    html, plugins = utils.text.process(entry.content,
                                       entry,
                                       notebook_url)
    
    processed_entry = {
        'id': entry.id,
        'notebook': {
            'slug': entry.notebook.slug,
            'name': entry.notebook.name
            },
        'date': entry.date,
        'content': entry.content,
        'html': Markup(html),
        'plugins': plugins,
    }

    return processed_entry
