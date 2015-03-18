# SmartyPants plugin
# Formats text through SmartyPants

from smartypants import smartyPants

def process(content, entry, notebook_url):
    return smartyPants(content)
