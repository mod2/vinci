# Poetry plugin
#
# Usage:
#
#    {poetry
#    &rsquo;Twas brillig, and the slithy toves
#      Did gyre and gimble in the wabe:
#    All mimsy were the borogoves,
#      And the mome raths outgrabe.
#
#    "Beware the Jabberwock, my son!
#      The jaws that bite, the claws that catch!
#    Beware the Jubjub bird, and shun
#      The frumious Bandersnatch!"
#    }
#
# - Blank line for new stanza
# - Two spaces to indent (or four, or six)
# - Quotes get curled, but Markdown isn't applied (use HTML tags)

import re

# Convert the poetry syntax to HTML
def poemify(m):
    content = m.group(1)

    html = '<div class="poetry">'

    # First split into stanzas
    stanzas = content.split('\n\n')

    for stanza in stanzas:
        lines = stanza.split('\n')
        for index, line in enumerate(lines):
            classes = []

            # If we're on the first line of a stanza, say so
            if index == 0:
                classes.append('stanza')

            # Get the indentation level (number of spaces at front, two spaces per level)
            indent_level = (len(line) - len(line.lstrip())) / 2
            if indent_level > 0:
                classes.append('indent-%s' % indent_level)

            # Set the class string
            if len(classes) > 0:
                class_str = ' class="%s"' % ' '.join(classes)
            else:
                class_str = ''

            html += '<p%s>%s</p>' % (class_str, line.strip())

    html += '</div>'

    return html

def process(content, notebook_url):
    # Convert {poetry ... } notation to the HTML we need
    regex = re.compile(r'{poetry\n(.*?)\n}', flags=re.DOTALL)
    content = regex.sub(poemify, content)

    return content
