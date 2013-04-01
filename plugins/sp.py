# SmartyPants plugin
# Formats text through SmartyPants

from smartypants import smartyPants

def process(content, notebook_url):
    return smartyPants(content)
