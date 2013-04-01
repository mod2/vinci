# Markdown plugin
# Formats text through Markdown

from markdown import markdown

def process(content, notebook_url):
    return markdown(content)
