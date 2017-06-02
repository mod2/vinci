import re
import os.path

from django.conf import settings

from vinci.models import Notebook

def get_or_create_notebook(notebook_slug):
    try:
        # Get
        notebook = Notebook.objects.get(slug=notebook_slug)
    except Exception as e:
        # Create
        notebook = Notebook()
        notebook.slug = notebook_slug
        notebook.name = ' '.join([x.capitalize() for x in notebook_slug.split('-')])
        notebook.order = 0
        notebook.save()

    return notebook

def parse_payload(payload):
    """ Parses a payload and returns dictionary with content + metadata. """

    response = {
        'content': '',
    }

    for line in payload.split('\n'):
        if len(line.strip()) > 0:
            # See if it's a notebook selector
            if line[0:2] == '::':
                # ::notebook
                notebook = line[2:]

                response['notebook'] = notebook.strip()

            elif line[0] == ':':
                # Normal metadata (:title Title)
                command_list = line[1:].split(' ')
                command = command_list[0]
                value = ' '.join(command_list[1:])

                if command == 'tag' or command == 'tags':
                    response['tags'] = [x.strip() for x in value.split(',')]
                else:
                    response[command] = value
            
            else:
                # Normal line
                response['content'] += '{}\n'.format(line.rstrip())

        else:
            # Blank line
            response['content'] += '\n'

    # Strip the content
    response['content'] = response['content'].strip()

    return response

def load_modes(modes, base):
    response = {}

    # Load modes
    for key in modes:
        response[key] = {
            'detail': '',
            'list': '',
            'search': '',
        }

        # Load detail first
        detail_filename = '{}_detail.html'.format(key)
        filename = '{}/{}'.format(base, detail_filename)
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                data = f.read()
            response[key]['detail'] = data

        # Load list
        list_filename = '{}_list.html'.format(key)
        filename = '{}/{}'.format(base, list_filename)
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                data = f.read()
            response[key]['list'] = data

        # Load search
        search_filename = '{}_search.html'.format(key)
        filename = '{}/{}'.format(base, search_filename)
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                data = f.read()
            response[key]['search'] = data
    
    return response

def load_template_for_mode(template, mode):
    """ Takes 'list' or 'detail' plus a mode and returns the combined template. """

    try:
        mode_html = ''

        if template in ['list', 'search']:
            slug = 'entries'
        elif template == 'detail':
            slug = 'entry'

        # Load the template HTML
        filename = '{}/vinci/templates/vinci/{}.html'.format(settings.BASE_DIR, slug)

        with open(filename, 'r') as f:
            data = f.read()

        # Default mode
        if mode == '' or mode not in settings.VINCI_MODES:
            mode = 'log'

        # Make sure we have this kind of a template
        if template in settings.VINCI_MODES[mode]:
            mode_html = settings.VINCI_MODES[mode][template]

        if mode_html == '':
            # Fallback to other defaults
            if template == 'list':
                # Use detail instead
                mode_html = settings.VINCI_MODES[mode]['detail']
            elif template == 'search':
                # Use log search instead
                mode_html = settings.VINCI_MODES['log']['search']
            else:
                # Use log detail instead
                mode_html = settings.VINCI_MODES['log']['detail']

        # Replace stubs
        data = re.sub(r"%%%STUB%%%", mode_html, data)
        data = re.sub(r"%%%EDITMODE%%%", settings.VINCI_EDIT_MODE_HTML, data)
        data = re.sub(r"%%%ENTRYSTART%%%", settings.VINCI_ENTRY_START_HTML, data)
        data = re.sub(r"%%%ENTRYEND%%%", settings.VINCI_ENTRY_END_HTML, data)
    except:
        data = ''

    return data
