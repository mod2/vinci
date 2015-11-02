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