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

    exclude_list = []
    plugin_list = []

    # Split by ----
    # Go through each line in metadata and parse
    # Strip off metadata

    # Check for entry-specific plugins
    lines = content.split('\n')
    if lines[0][:8] == 'plugins:':
        plugin_list = [x.strip() for x in lines[0][8:].split(',')]
        content = '\n'.join(lines[1:])
        
        # Go through the list and apply each one
        for plugin_name in plugin_list:
            name = str(plugin_name)

            # If the name starts with - ('-md', etc.), add to exclude list for default plugins
            if name[0] == '-':
                exclude_list.append(name[1:])
            elif name in config.plugins:
                # Otherwise run the plugin
                content = run_plugin(name, content, notebook_url)
    
    # Run default plugins last
    for plugin_name in config.default_plugins:
        name = str(plugin_name)
        if name not in exclude_list:
            content = run_plugin(name, content, notebook_url)

    return content, plugin_list
