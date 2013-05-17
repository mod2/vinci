# Text-related utility functions

import config
import vinci.utils
import re


def run_plugin(name, content, entry, notebook_url):
    # Import the plugin function
    plugins = __import__("plugins", fromlist=[name])
    plugin = getattr(plugins, name)

    # Process it
    return plugin.process(content, entry, notebook_url)


def parse_header(content):
    response = {
        'content': content,
        'title': '',
        'slug': '',
        'plugins': [],
        'tags': []
    }

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
                response['plugins'] = [x.strip() for x in value.split(',')]

            if keyword == 'title':
                response['title'] = value
                response['slug'] = vinci.utils.slugify(response['title'])

            if keyword == 'slug':
                response['slug'] = value

            if keyword == 'tags' or keyword == 'tag':
                response['tags'] = [x.strip() for x in value.split(',')]

        # If there is a header, the content now is the rest after the header
        # Otherwise leave it intact
        response['content'] = body[1]

    return response


def process(content, entry, notebook_url):
    """Process an entry for display in HTML."""

    exclude_list = []

    response = parse_header(content)

    # Go through the list (if present) and apply each plugin
    for plugin_name in response['plugins']:
        name = str(plugin_name)

        # If the name starts with - ('-md', etc.), add to exclude list
        # for default plugins
        if name[0] == '-':
            exclude_list.append(name[1:])
        elif name in config.plugins:
            # Otherwise run the plugin
            response['content'] = run_plugin(name,
                                             response['content'],
                                             entry,
                                             notebook_url)

    # Check for entry-specific plugins
    # lines = content.split('\n')
    # Run default plugins last
    for plugin_name in config.default_plugins:
        name = str(plugin_name)
        if name not in exclude_list:
            response['content'] = run_plugin(name,
                                             response['content'],
                                             entry,
                                             notebook_url)

    # Pull in any hashtags from the content
    m = re.findall(r"#(\w+)", response['content'])
    for tag in m:
        if tag not in response['tags']:
            response['tags'].append(tag)

    return response
