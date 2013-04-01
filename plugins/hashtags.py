# Hashtags plugin
# Converts hashtags to links

import re

def process(content, notebook_url):
    """ Convert hashtags to links """

    return re.sub(r"#(\w+)", r'<a href="%s/tag/\1" class="tag">#\1</a>' % notebook_url, content)
