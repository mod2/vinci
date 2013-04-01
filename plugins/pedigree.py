# Pedigree plugin

import re

def process(content):
    # Get rid of the plugins line
    str = '\n'.join(content.split('\n')[1:])

    # Change things over
    regex = re.compile(r'{pedigree\n(.*?)\n}', flags=re.DOTALL)
    str = regex.sub(r'<div class="emperor-pedigree">\1</div>', str)

    return str
