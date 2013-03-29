# Text-related utility functions

from markdown import markdown
from smartypants import smartyPants
import re

def markdownify(content, url, slug, base_url):
    """Everything needed to prep an entry for display (hashtag conversion,
       Markdown, and SmartyPants)"""

    html = convert_hashtags(content, url, slug, base_url)
    return smartyPants(markdown(html))


def convert_hashtags(value, index, slug, base_url):
    """ Convert hashtags to links """

    url = '%s%s%s' % (index, slug, base_url)

    return re.sub(r"#(\w+)", r'<a href="%s/\1" class="tag">#\1</a>' % url, value)
