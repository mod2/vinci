# Page link plugin
#
# Usage:
#   [[link text | page-slug]]
#   [[link text | notebook/page-slug]]

import re
import string
from flask import url_for

def parse_match(m):
    link_text = m.group(1)
    if m.group(2) and m.group(2) != '':
        notebook = m.group(2)[:-1]
    else:
        notebook = 'PLEASEREPLACEME'    # placeholder
    page_slug = m.group(3)

    link_html = '[%s](/%s/entry/%s)' % (link_text, notebook, page_slug)

    return link_html

def process(content, entry, notebook_url):
    # Do the bulk of the work here
    content = re.sub(r'\[\[\s*(.*?)\s*\|\s*(.*?/)?(.*?)\s*\]\]', parse_match, content)

    # Replace the placeholder with the current notebook's slug
    # (Since we can't pass the slug in to parse_match)
    content = string.replace(content, 'PLEASEREPLACEME', entry.notebook.slug)

    return content
