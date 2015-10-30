from vinci.models import Notebook, Section

def get_sections_for_notebook(notebook):
    sections = Section.objects.filter(notebook=notebook).order_by('name')

    return sections
