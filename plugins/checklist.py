# Checklist plugin
#
# Turns this:
#
#     * Item 1
#     * Item 2
#     * Item 3
#
# Into a list of checkboxes (todo list, etc.).

import re

def process(content):
    # Get rid of the plugins line
    str = '\n'.join(content.split('\n')[1:])

    # Change things over
    str = re.sub(r'\* (.*)', r'<div class="checklist-group"><input type=checkbox><label>\1</label></div>', str)

    return str
