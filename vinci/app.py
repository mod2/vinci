import vinci.models as m
import vinci.utils as utils
import config
import datetime

def db(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            m.init_db(config.database_file)
        return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper

@db
def add_notebook(name, description=None):
    """Add a new notebook."""
    nb = m.Notebook(name=name, description=description)
    nb.slug = utils.slugify(nb.name)
    nb.save()
    return nb

@db
def rename_notebook(notebook_slug, name):
    """Rename a notebook."""
    try:
        nb = m.Notebook.get(m.Notebook.slug == notebook_slug)
        nb.name = name
        nb.slug = utils.slugify(nb.name)
        nb.save()

        return nb
    except:
        return False

@db
def delete_notebook(notebook_slug):
    """Delete a notebook."""
    try:
        # First delete the entries
        entries = get_entries(notebook_slug)
        for entry in entries:
            entry.delete_instance()

        # Then the notebook
        nb = m.Notebook.get(m.Notebook.slug == notebook_slug)
        nb.delete_instance()
        return True
    except m.Notebook.DoesNotExist:
        return False

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
    entry = m.Entry.get(id=id)

    # Update the content
    entry.content = content

    # Revise the date if passed in
    if date:
        entry.date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

    entry.save()

    return entry

# Delete an entry
@db
def delete_entry(id, notebook_slug):
    try:
        entry = m.Entry.get(m.Entry.id == id)
        entry.delete_instance()
        return True
    except m.Entry.DoesNotExist:
        return False

# Get all entries for the given notebook
@db
def get_entries(notebook_slug):
    return get_notebook(notebook_slug).entries

# Get a specific entry
@db
def get_entry(id, notebook_slug):
    return m.Entry.get(m.Entry.id == id)
