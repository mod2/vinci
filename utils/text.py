# Text-related utility functions

import re
import config

def run_plugin(name, content, notebook_url):
    # Import the plugin function
    plugins = __import__("plugins", fromlist=[name])
    plugin = getattr(plugins, name)

    # Process it
    return plugin.process(content, notebook_url)

def process(content, notebook_url):
    """Process an entry for display in HTML."""

    # Check for entry-specific plugins
    plugin_list = []
    lines = content.split('\n')
    if lines[0][:8] == 'plugins:':
        plugin_list = [x.strip() for x in lines[0][8:].split(',')]
        content = '\n'.join(lines[1:])
        
        # Go through the list and apply each one
        for plugin_name in plugin_list:
            name = str(plugin_name)
            if name in config.plugins:
                content = run_plugin(name, content, notebook_url)
    
    # Run default plugins last
    for plugin_name in config.default_plugins:
        name = str(plugin_name)
        content = run_plugin(name, content, notebook_url)

    # Convert hashtags to HTML links
    #html = convert_hashtags(content, url, slug, base_url)

    # Markdown and SmartyPants it and return it
    #return (smartyPants(markdown(html)), plugin_list)
    return content, plugin_list


def convert_hashtags(value, index, slug, base_url):
    """ Convert hashtags to links """

    url = '%s%s%s' % (index, slug, base_url)

    return re.sub(r"#(\w+)", r'<a href="%s/\1" class="tag">#\1</a>' % url, value)
