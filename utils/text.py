# Text-related utility functions

import re
import config
import vinci.utils

def run_plugin(name, content, entry, notebook_url):
    # Import the plugin function
    plugins = __import__("plugins", fromlist=[name])
    plugin = getattr(plugins, name)

    # Process it
    return plugin.process(content, entry, notebook_url)

def process(content, entry, notebook_url):
    """Process an entry for display in HTML."""

    exclude_list = []
    plugin_list = []
    title = ''
    slug = ''

    # Split entry by ----
    body = content.split('----')

    # If there's a header
    if len(body) > 1:
        # Parse the header
        header_lines = body[0].split('\n')

        for line in header_lines:
            # Get the keyword
            keyword = line.split(':')[0].strip()

            # Get the value (and keep existing colons)
            value = ':'.join(line.split(':')[1:]).strip()

            if keyword == 'plugins' or keyword == 'plugin':
                plugin_list = [x.strip() for x in value.split(',')]

            if keyword == 'title':
                title = value
                slug = vinci.utils.slugify(title)

            if keyword == 'slug':
                slug = value

        # If there is a header, the content now is the rest after the header
        # Otherwise leave it intact
        content = body[1]

    # Go through the list (if present) and apply each plugin
    for plugin_name in plugin_list:
        name = str(plugin_name)

        # If the name starts with - ('-md', etc.), add to exclude list for default plugins
        if name[0] == '-':
            exclude_list.append(name[1:])
        elif name in config.plugins:
            # Otherwise run the plugin
            content = run_plugin(name, content, entry, notebook_url)

    # Check for entry-specific plugins
    lines = content.split('\n')
    # Run default plugins last
    for plugin_name in config.default_plugins:
        name = str(plugin_name)
        if name not in exclude_list:
            content = run_plugin(name, content, entry, notebook_url)

    response = {
        'content': content,
        'title': title,
        'slug': slug,
        'plugins': plugin_list
    }

    return response
