# Markdown plugin
# Formats text through Markdown

from mistune import markdown


def process(content, entry, notebook_url):
    return markdown(content, extensions=['markdown.extensions.fenced_code'])
