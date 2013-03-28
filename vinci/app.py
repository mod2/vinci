import vinci.models as m
import vinci.utils as utils
import vinci.search_indexer as si
import config
import datetime


def init_db(database_file=config.database_file):
    """Initializes the database creating a connection."""
    m.init_db(database_file)


def add_notebook(name, description=None):
    """Add a new notebook."""
    nb = m.Notebook(name=name, description=description)
    nb.slug = utils.slugify(nb.name)
    nb.save()
    return nb


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
        m.db.execute_sql('VACUUM')
        return True
    except m.Notebook.DoesNotExist:
        return False


def get_notebook(notebook_slug):
    """Get a specific notebook"""
    return m.Notebook.get(m.Notebook.slug == notebook_slug)


def get_all_notebooks():
    """Get all notebooks"""
    notebooks = []

    for notebook in m.Notebook.select():
        notebooks.append(notebook)

    return notebooks


def add_entry(content, notebook_slug, date=None):
    """Add a new entry to a notebook."""
    nb = get_notebook(notebook_slug)
    if date is None:
        new_entry = m.Entry(content=content, notebook=nb)
    else:
        new_entry = m.Entry(content=content, notebook=nb, date=date)
    new_entry.save()
    si.add_or_update_index(new_entry)
    return new_entry


def edit_entry(id, content, notebook_slug, date=None):
    """Edit an entry."""
    entry = m.Entry.get(id=id)

    # Update the content
    entry.content = content

    # Revise the date if passed in
    if date:
        entry.date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

    entry.save()
    si.add_or_update_index(entry)

    return entry


def delete_entry(id, notebook_slug):
    """Delete an entry"""
    try:
        entry = m.Entry.get(m.Entry.id == id)
        si.delete_from_index(entry)
        entry.delete_instance()
        m.db.execute_sql('VACUUM')
        return True
    except m.Entry.DoesNotExist:
        return False


def get_entries(notebook_slug):
    """Get all entries for the given notebook"""
    return get_notebook(notebook_slug).entries


def get_entry(id, notebook_slug):
    """Get a specific entry"""
    return m.Entry.get(m.Entry.id == id)


def search(query):
    """Submit search to the whoosh searcher"""
    return si.search(query)


def reindex():
    """Perform a full index."""
    return si.full_index()
