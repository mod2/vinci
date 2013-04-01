# Grid plugin

import re

def process(content):
    # Get rid of the plugins line
    str = '\n'.join(content.split('\n')[1:])

    # Change things over
    regex = re.compile(r'{grid\n(.*?)\n}', flags=re.DOTALL)
    str = regex.sub(r'<div class="grid-box">\1</div>', str)

    return str
