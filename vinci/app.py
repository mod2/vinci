import vinci.models as m
import vinci.utils as utils
import config

def db(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            m.init_db(config.database_file)
        return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper

@db
def create_notebook(name, description=None):
    """Create a new notebook."""
    nb = m.Notebook(name=name, description=description)
    nb.slug = utils.slugify(nb.name)
    nb.save()
    return nb

# Get a specific notebook
@db
def get_notebook(notebook_slug):
    return m.Notebook.get(m.Notebook.slug == notebook_slug)

# Get all notebooks
@db
def get_all_notebooks():
    notebooks = []

    for notebook in m.Notebook.select():
        notebooks.append(notebook)

    return notebooks

# Add a new entry to a notebook
@db
def add_entry(content, notebook_slug, date=None):
    nb = get_notebook(notebook_slug)
    if date is None:
        new_entry = m.Entry(content=content, notebook=nb)
    else:
        new_entry = m.Entry(content=content, notebook=nb, date=date)
    new_entry.save()
    return new_entry

# Edit an entry
@db
def edit_entry(id, content, notebook_slug, date=None):
    entry = m.Entry.get(id=id, notebook=notebook_slug)

    entry.content = content

    if date:
        entry.date = date

    entry.save()

    return entry

# Get all entries for the given notebook
@db
def get_entries(notebook_slug):
    return get_notebook(notebook_slug).entries
