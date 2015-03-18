#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Language forms plugin

import re

# Example:
#
# {forms
#   classes: wide
#   labels: nom | acc | gen | dat
#   sg: iċ | mē, mec | mīn | mē
#   pl: wē | ūs | ūre | ūs
# }


# Convert the syntax to an HTML table
def convert(m):
    content = m.group(1)
    lines = content.split('\n')

    labels = []
    column_order = []
    columns = {}
    css_classes = ''

    for line in lines:
        # Strip whitespace
        line = line.strip()

        # Parse
        keyword, args = line.split(': ')
        args = [x.strip() for x in args.strip().split(' | ')]

        if keyword == 'labels':
            # It's the label definition list
            labels = args
        elif keyword == 'classes':
            # CSS classes to apply to the table
            css_classes = ' %s' % ' '.join(args)
        else:
            # It's a column
            column_order.append(keyword)
            columns[keyword] = args

    html = '<table class="forms%s">' % css_classes

    # Column labels
    html += '<tr>'
    html += '<th></th>'
    for column in column_order:
        html += '<th>%s</th>' % column
    html += '</tr>'

    for i, label in enumerate(labels):
        html += '<tr>'
        html += '<th>%s</th>' % label
        for column in column_order:
            if i < len(columns[column]):
                html += '<td>%s</td>' % columns[column][i]
            else:
                html += '<td></td>'
        html += '</tr>'

    html += '</table>'

    return html


def process(content, entry, notebook_url):
    # Convert {forms ... } notation to the HTML we need
    regex = re.compile(r'{forms\n(.*?)\n}', flags=re.DOTALL)
    content = regex.sub(convert, content)

    return content
