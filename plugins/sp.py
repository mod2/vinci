# SmartyPants plugin
# Formats text through SmartyPants

from smartypants import smartypants


def process(content, entry, notebook_url):
    return smartypants(content)
