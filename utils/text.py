# Text-related utility functions

from markdown import markdown
from smartypants import smartyPants
import re
import config

def markdownify(content, url, slug, base_url):
    """Everything needed to prep an entry for display (plugins,
       hashtag conversion, Markdown, and SmartyPants)"""

    # Check for plugins
    plugin_list = []
    lines = content.split('\n')
    if lines[0][:8] == 'plugins:':
        plugin_list = lines[0][8:].split(',')
        content = '\n'.join(lines[1:])
        
        # Go through the list and apply each one
        for plugin_name in plugin_list:
            name = str(plugin_name)
            if name in config.plugins:
                # Import the plugin function
                plugins = __import__("plugins", fromlist=[name])
                plugin = getattr(plugins, name)

                # Process it
                content = plugin.process(content)
    
    # Convert hashtags to HTML links
    html = convert_hashtags(content, url, slug, base_url)

    # Markdown and SmartyPants it and return it
    return (smartyPants(markdown(html)), plugin_list)


def convert_hashtags(value, index, slug, base_url):
    """ Convert hashtags to links """

    url = '%s%s%s' % (index, slug, base_url)

    return re.sub(r"#(\w+)", r'<a href="%s/\1" class="tag">#\1</a>' % url, value)
