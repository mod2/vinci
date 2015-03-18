# Pedigree plugin

import re

def process(content, entry, notebook_url):
    # Convert to Emperor syntax
    regex = re.compile(r'{pedigree\n(.*?)\n}', flags=re.DOTALL)
    content = regex.sub(r'<div class="emperor-pedigree">\1</div>', content)

    return content
