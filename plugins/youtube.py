# YouTube plugin
# Converts YouTube links to embedded videos

import re

def process(content, notebook_url):
    content = re.sub(r'http://www.youtube.com/watch\?v=(.*)', r'<iframe width="640" height="360" src="http://www.youtube.com/embed/\1" frameborder="0" allowfullscreen></iframe>', content)

    return content
