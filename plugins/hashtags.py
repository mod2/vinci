# Hashtags plugin
# Converts hashtags to links

import re


def process(content, entry, notebook_url):
    """ Convert hashtags to links """

    return re.sub(r"(\s)#(\w+)",
                  (r'\1<a href="{}/tag/\2" class="tag">#\2</a>'
                   .format(notebook_url)),
                  content)
