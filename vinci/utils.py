import re
import os.path

from django.conf import settings

from vinci.models import Notebook, Section

def get_sections_for_notebook(notebook):
    sections = Section.objects.filter(notebook=notebook).order_by('name')

    return sections

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

def get_or_create_section(section_slug, notebook_slug):
    # First get the notebook
    notebook = get_or_create_notebook(notebook_slug)

    try:
        # Get section
        section = Section.objects.get(slug=section_slug, notebook=notebook)
    except Exception as e:
        # Create section
        section = Section()
        section.slug = section_slug
        section.name = ' '.join([x.capitalize() for x in section_slug.split('-')])
        section.order = 0
        section.notebook = notebook
        section.save()

    return section

def parse_payload(payload):
    """ Parses a payload and returns dictionary with content + metadata. """

    response = {
        'content': '',
    }

    for line in payload.split('\n'):
        if len(line.strip()) > 0:
            # See if it's a notebook selector
            if line[0:2] == '::':
                selector = line[2:]
                # ::notebook/section OR ::notebook
                if '/' in selector:
                    notebook, section = selector.split('/')
                else:
                    notebook = selector
                    section = None

                response['notebook'] = notebook.strip()
                if section:
                    response['section'] = section.strip()

            elif line[0] == ':':
                # Normal metadata (:title Title)
                command_list = line[1:].split(' ')
                command = command_list[0]
                value = ' '.join(command_list[1:])

                if command == 'tag' or command == 'tags':
                    response[command] = [x.strip() for x in value.split(',')]
                else:
                    response[command] = value
            
            else:
                # Normal line
                response['content'] += '{}\n'.format(line.strip())

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
        }

        # Load detail first
        detail_filename = '{}_detail.html'.format(key)
        if detail_filename != '':
            filename = '{}/{}'.format(base, detail_filename)
            if os.path.isfile(filename):
                with open(filename, 'r') as f:
                    data = f.read()
                response[key]['detail'] = data

        # Load list
        list_filename = '{}_list.html'.format(key)
        if list_filename == '':
            # Use detail
            response[key]['list'] = response[key]['detail']
        else:
            # Load list
            filename = '{}/{}'.format(base, list_filename)
            if os.path.isfile(filename):
                with open(filename, 'r') as f:
                    data = f.read()
                response[key]['list'] = data

    return response

def load_template_for_mode(template, mode):
    """ Takes 'list' or 'detail' plus a mode and returns the combined template. """

    try:
        mode_html = ''

        if template == 'list':
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
