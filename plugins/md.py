# Markdown plugin
# Formats text through Markdown

from markdown import markdown

def process(content, entry, notebook_url):
    return markdown(content, extensions=['markdown.extensions.fenced_code'])
