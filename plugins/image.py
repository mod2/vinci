# Image plugin
#
# Usage: ((image.png))
#
# Automatically looks in the static/YYYY/MM directory using the entry date

import re
from django.conf import settings

def process(content, entry, notebook_url):
    content = re.sub(r'\(\((.*?)\)\)',
                     r'<figure><img src="{}/{:04}/{:02}/\1" alt="\1" /></figure>'.format(
                         settings.VINCI_IMAGE_BASE_URL,
                         entry.date.year,
                         entry.date.month
                         ),
                     content
                     )

    return content
