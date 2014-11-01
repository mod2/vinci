import models as m
import utils as utils
import search_indexer as si
import config
import datetime
import math


def init_db(database_file=config.database_file, admin=config.admin):
    """Initializes the database creating a connection."""
    m.init_db(database_file, admin)
    si.get_or_create_index()


def add_notebook(name, description=None):
    """Add a new notebook."""
    nb = m.Notebook(name=name, description=description)
    nb.slug = utils.slugify(nb.name)
    nb.save()
    return nb


def edit_notebook(notebook_slug, name, description=None):
    """Edit a notebook."""
    try:
        nb = m.Notebook.get(m.Notebook.slug == notebook_slug)

        nb.name = name
        nb.slug = utils.slugify(nb.name)

        if description:
            nb.description = description

        nb.save()

        return nb
    except:
        return False


def delete_notebook(notebook_slug):
    """Delete a notebook."""
    try:
        # First delete the entries
        entries, hits, pages = get_entries(notebook_slug)
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


def add_entry(content, notebook_slug, date=None, title='', slug=''):
    """Add a new entry to a notebook."""
    nb = get_notebook(notebook_slug)
    kwargs = {'notebook': nb}
    if date is not None:
        kwargs['date'] = date
    new_entry = m.Entry(**kwargs)
    new_entry.save()

    new_revision = m.Revision()
    new_revision.content = content
    new_revision.title = title
    new_revision.slug = slug
    new_revision.save()

    new_entry.current_revision = new_revision
    new_entry.save()
    si.add_or_update_index(new_entry, new=True)
    return new_entry


def edit_entry(id, content, notebook_slug, date=None, title='', slug=''):
    """Edit an entry."""
    entry = m.Entry.get(id=id)
    new_revision = m.Revision()

    # Update the content
    new_revision.content = content
    new_revision.title = title
    new_revision.slug = slug
    new_revision.parent = entry.current_revision
    new_revision.save()

    # Revise the date if passed in
    if date:
        entry.date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

    entry.current_revision = new_revision

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


def append_today_entry(content, notebook_slug):
    """Append/create today's entry."""

    # See if we have an entry today
    try:
        # Today
        now = datetime.datetime.now()
        today = datetime.datetime(now.year, now.month, now.day)
        tomorrow = today + datetime.timedelta(days=1)

        # Notebook
        nb = get_notebook(notebook_slug)

        # Get first entry for today
        results = m.Entry.select()
        results = results.where(m.Entry.notebook == nb)
        results = results.where((m.Entry.date >= today) & (m.Entry.date <= tomorrow))
        results = results.order_by(m.Entry.date.asc())
        results = results.limit(1)

        if results.count() == 0:
            raise m.Entry.DoesNotExist
        else:
            entry = results[0]

        # Get the text
        cur_rev = entry.current_revision

        # Add new revision with appended content
        new_revision = m.Revision()
        new_revision.content = cur_rev.content + content
        new_revision.save()

        # Save the entry
        entry.current_revision = new_revision
        entry.save()

        si.add_or_update_index(entry)
    except m.Entry.DoesNotExist:
        # We don't have an entry today, so create it
        entry = add_entry(content, notebook_slug)

    return entry


def get_entries(notebook_slug,
                sort=config.default_sort_order,
                page=1,
                num_per_page=config.results_per_page):
    """Get all entries for the given notebook"""
    entries = get_notebook(notebook_slug).entries
    if sort == 'date_asc':
        entries = entries.order_by(m.Entry.date.asc())
    total_entries = entries.count()
    total_pages = math.ceil(total_entries / float(num_per_page))
    return entries.paginate(page, num_per_page), total_entries, total_pages


def get_entry(notebook_slug='', id=-1, slug=''):
    """Get a specific entry"""
    nb = None
    if notebook_slug != '':
        nb = get_notebook(notebook_slug)

    if id != -1 and nb is not None:
        return m.Entry.get(m.Entry.id == id, m.Entry.notebook == nb)
    elif slug != '' and nb is not None:
        query = m.Entry.select(m.Entry, m.Revision).join(m.Revision)
        entries = [e for e in query.where(m.Revision.slug == slug, m.Entry.notebook == nb)]
        if entries:
            return entries[0]
        else:
            raise m.Entry.DoesNotExist()
    elif nb is None and slug != '':
        query = m.Entry.select(m.Entry, m.Revision).join(m.Revision)
        entries = [e for e in query.where(m.Revision.slug == slug)]
        if entries:
            return entries[0]
        else:
            raise m.Entry.DoesNotExist()
    else:
        return None


def search(query, page=1, sort_order='relevance'):
    """Submit search to the whoosh searcher"""
    page_results, total_hits, total_pages = si.search(query,
                                                      page,
                                                      config.results_per_page,
                                                      sort_order)
    ids = [entry_id for entry_id, __ in page_results.items()]
    entries = m.Entry.select().where(m.Entry.id << ids)
    results = []

    for entry in entries:
        entry.excerpt = page_results[entry.id][1]
        results.append((page_results[entry.id][0], entry))
    results.sort()  # depends on sort
    return [entry for rank, entry in results], total_hits, total_pages


def reindex():
    """Perform a full index."""
    return si.full_index()


def get_user(username):
    try:
        return m.User.get(m.User.username == username)
    except:
        return None


def get_new_user():
    return m.User()
