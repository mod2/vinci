# Page link plugin
#
# Usage:
#   [[link text | page-slug]]
#   [[link text | notebook/section/page-slug]]

import re


def parse_match(m):
    link_text = m.group(1)

    if m.group(2) and m.group(2) != '':
        notebook = m.group(2)[:-1]
    else:
        notebook = 'REPLACENOTEBOOK'    # placeholder

    if m.group(3) and m.group(3) != '':
        section = m.group(3)[:-1]
    else:
        section = 'REPLACESECTION'    # placeholder

    page_slug = m.group(4)

    link_html = '[{}](/{}/{}/{}/)'.format(link_text, notebook, section, page_slug)

    return link_html


def process(content, entry, notebook_url):
    # Do the bulk of the work here
    content = re.sub(r'\[\[\s*(.*?)\s*\|\s*(.*?/)?(.*?/)?(.*?)\s*\]\]',
                     parse_match, content)

    # Replace the placeholder with the current notebook/section slugs
    # (Since we can't pass the slugs in to parse_match)
    content = content.replace('REPLACENOTEBOOK', entry.notebook.slug)
    content = content.replace('REPLACESECTION', entry.section.slug)

    return content
