# Image plugin
#
# Usage: ((image.png))
#
# Automatically looks in the static/YYYY/MM directory using the entry date

import re
from flask import url_for

def process(content, entry, notebook_url):
    content = re.sub(r'\(\((.*?)\)\)', r'<figure><img src="%sstatic/images/%04d/%02d/\1" alt="\1" /></figure>' % (url_for('index'), entry.date.year, entry.date.month), content)

    return content
