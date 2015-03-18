# Grid plugin

import re

# Convert the 010100 etc. syntax to an HTML table
def gridify(m):
    content = m.group(1)
    lines = content.split('\n')

    html = '<div class="grid-box">'
    html += '<table>'

    for line in lines:
        html += '<tr>'
        for char in line:
            html += '<td%s></td>' % (' class="filled"' if char == '1' else '')
        html += '</tr>'
    html += '</table>'
    html += '</div>'

    return html

def process(content, entry, notebook_url):
    # Convert {grid ... } notation to the HTML we need
    regex = re.compile(r'{grid\n(.*?)\n}', flags=re.DOTALL)
    content = regex.sub(gridify, content)

    return content
