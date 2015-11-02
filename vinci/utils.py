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
