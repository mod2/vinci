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

def process(content, entry, notebook_url):
    # Convert to checkboxes
    content = re.sub(r'\* (.*)', r'<div class="checklist-group"><input type=checkbox><label>\1</label></div>', content)

    return content

