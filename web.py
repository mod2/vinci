# Vinci web app

from flask import (Flask,
                   request,
                   url_for,
                   send_from_directory,
                   jsonify,
                   redirect,
                   session,
                   g,
                   flash)
from flask.ext.openid import OpenID
from datetime import datetime
import os
from os.path import join, dirname
import re
import logging

import config
import vinci
from vinci.models import Entry
import utils.text
import utils.entries
import utils.pagination
import utils.template
from access_utils import admin_only, notebook_access, ws_access

# set up some debugging stuff
if config.debug:
    # Set up some logging stuff
    logger = logging.getLogger('simple_example')
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler(config.log_file)
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - \
                                  %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

GOOGLE_OPENID_URL = 'https://www.google.com/accounts/o8/id'

# Initialize the Flask app
app = Flask('Vinci')
config.root_path = app.root_path
app.secret_key = config.secret_key
oid = OpenID(app, join(dirname(__file__), config.openid_store))

# Initialize database
vinci.init_db()


def get_user():
    """Get the current user object if one exists.
    :returns: User object
    """
    return vinci.get_user(session.get('openid-email', ''))


def response_with_callback(response, callback):
    """Redirect if callback, otherwise return JSONed response."""
    if callback:
        return redirect(callback)
    else:
        return jsonify(response)


# callbacks
@app.before_request
def lookup_current_user():
    """Store the currently authenticated user to the global session
    before each request."""
    g.user = get_user()


@oid.after_login
def create_user(resp):
    """After successfull login (oid) make sure there is a user that
    matches the use in the database."""
    session['openid'] = resp.identity_url
    session['openid-email'] = resp.email
    if get_user() is None:
        new_user = vinci.get_new_user()
        new_user.username = resp.email
        new_user.display = resp.email
        new_user.save()
    return redirect(oid.get_next_url())


#Static routes
@app.route('/favicon.ico/')
def favicon():
    """Serve up the favicon."""
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


#routes
@app.route('/login/')
@oid.loginhandler
def login():
    if g.user is not None:
        return redirect(oid.get_next_url())
    else:
        return oid.try_login(session.get('openid', GOOGLE_OPENID_URL),
                             ask_for=['email'])


@app.route('/logout/')
def logout():
    session.pop('openid', None)
    session.pop('openid-email', None)
    flash(u'You are now signed out.')
    return redirect(oid.get_next_url())


@app.route('/nopermission/')
def no_permission():
    return "Not authorized"


@app.route('/add/entry/', methods=['GET', 'POST'])
@ws_access
def add_entry():
    """Add an entry."""
    # Defaults and parameters
    notebook = request.args.get('notebook')
    date = request.args.get('date')
    callback = request.args.get('callback')

    if request.method == 'POST':
        content = request.form['content']
    else:
        content = request.args.get('content')

    # If the date is a string, convert it to datetime first
    if date and isinstance(date, unicode):
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    elif date and isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

    header = utils.text.parse_header(content)

    # Add the entry
    entry = vinci.add_entry(content=content,
                            notebook_slug=notebook,
                            date=date,
                            title=header['title'],
                            slug=header['slug'])

    # If we succeeded
    if entry:
        # Prep the HTML
        response = utils.text.process(content,
                                      entry,
                                      '%s%s' % (url_for('index'), notebook))

        # Send the info we need to generate the entry HTML
        response = {
            'status': 'success',
            'id': entry.id,
            'url': '%s.%s' % (entry.date.strftime('%Y-%m-%d'), entry.id),
            'date': entry.date.strftime('%-m.%-d.%y'),
            'time': entry.date.strftime('%l:%M %p').strip().lower(),
            'datetime': entry.date.strftime('%Y-%m-%d %H:%M:%S'),
            'html': response['content'],
            'content': content,
            'title': response['title'],
            'slug': response['slug'],
            'tags': response['tags'],
            'plugins': response['plugins'],
        }

        return response_with_callback(response, callback)
    else:
        response = {'status': 'error'}

        return jsonify(response)


@app.route('/delete/entry/')
@ws_access
def delete_entry():
    """Delete an entry."""
    # Defaults and parameters
    notebook = request.args.get('notebook')
    id = request.args.get('id')
    callback = request.args.get('callback')
    #type = request.args.get('type') or 'json'

    # Delete the entry
    success = vinci.delete_entry(id=id, notebook_slug=notebook)

    # If we succeeded
    if success:
        response = {'status': 'success'}

        return response_with_callback(response, callback)
    else:
        response = {'status': 'error'}

        return jsonify(response)


# TODO: refactor this, lots of shared code with add_entry()
@app.route('/edit/entry/', methods=['GET', 'POST'])
@ws_access
def edit_entry():
    """Edit an entry."""
    # Defaults and parameters
    notebook = request.args.get('notebook')
    id = request.args.get('id')
    date = request.args.get('date')
    callback = request.args.get('callback')

    if request.method == 'POST':
        content = request.form['content']
    else:
        content = request.args.get('content')

    # Parse the header
    header = utils.text.parse_header(content)

    # Edit the entry
    entry = vinci.edit_entry(id=id,
                             content=content,
                             notebook_slug=notebook,
                             date=date,
                             title=header['title'],
                             slug=header['slug'])

    # If we succeeded
    if entry:
        # Prep the HTML
        response = utils.text.process(content,
                                      entry,
                                      '%s%s' % (url_for('index'), notebook))

        # Send the info we need to generate the entry HTML
        response = {
            'status': 'success',
            'id': entry.id,
            'url': '%s.%s' % (entry.date.strftime('%Y-%m-%d'), entry.id),
            'date': entry.date.strftime('%-m.%-d.%y'),
            'time': entry.date.strftime('%l:%M %p').strip().lower(),
            'datetime': entry.date.strftime('%Y-%m-%d %H:%M:%S'),
            'html': response['content'],
            'content': content,
            'title': response['title'],
            'slug': response['slug'],
            'tags': response['tags'],
            'plugins': response['plugins'],
        }

        return response_with_callback(response, callback)
    else:
        response = {'status': 'error'}

        return jsonify(response)


@app.route('/add/notebook/')
@ws_access
def add_notebook():
    """Add a notebook."""
    # Defaults and parameters
    name = request.args.get('name')
    description = request.args.get('description')
    callback = request.args.get('callback')
    #type = request.args.get('type') or 'json'

    # Add the notebook
    notebook = vinci.add_notebook(name=name, description=description)

    # If we succeeded
    if notebook:
        response = {
            'status': 'success',
            'name': notebook.name,
            'slug': notebook.slug,
            'description': notebook.description
        }

        return response_with_callback(response, callback)
    else:
        response = {'status': 'error'}

        return jsonify(response)


@app.route('/delete/notebook/')
@ws_access
def delete_notebook():
    """Delete a notebook."""
    # Defaults and parameters
    notebook = request.args.get('notebook')
    callback = request.args.get('callback')
    #type = request.args.get('type') or 'json'

    # Delete the entry
    success = vinci.delete_notebook(notebook_slug=notebook)

    # If we succeeded
    if success:
        response = {'status': 'success'}

        return response_with_callback(response, callback)
    else:
        response = {'status': 'error'}

        return jsonify(response)


@app.route('/edit/notebook/')
@ws_access
def edit_notebook():
    """Edit a notebook."""
    # Defaults and parameters
    notebook = request.args.get('notebook')
    name = request.args.get('name')
    description = request.args.get('description')
    callback = request.args.get('callback')
    #type = request.args.get('type') or 'json'

    # Edit the entry
    notebook = vinci.edit_notebook(notebook_slug=notebook,
                                   name=name,
                                   description=description)

    # If we succeeded
    if notebook:
        response = {
            'status': 'success',
            'name': notebook.name,
            'slug': notebook.slug,
            'description': notebook.description
        }

        return response_with_callback(response, callback)
    else:
        response = {'status': 'error'}

        return jsonify(response)


@app.route('/reindex/')
@admin_only
def reindex():
    """Reindex the index."""
    vinci.reindex()
    return redirect(url_for('index'))


@app.route('/search/<query>')
@admin_only
def search_all_notebooks(query):
    """Search within all notebooks."""
    # Defaults and parameters
    type = request.args.get('type', 'html')
    sortby = request.args.get('sort', config.default_search_order)
    page = int(request.args.get('page', 1))

    # Data
    display_query = re.sub(r'tags:', '#', query)
    db_entries, total_hits, total_pages = vinci.search(query, page, sortby)
    entries = utils.entries.process_entries(db_entries)

    base_url = '%ssearch/%s' % (url_for('index'), query)
    pagination = utils.pagination.get_pagination(page,
                                                 total_hits,
                                                 total_pages,
                                                 sortby,
                                                 base_url)

    return utils.template.render('list',
                                 type,
                                 title="Search All Notebooks",
                                 query=display_query,
                                 entries=entries,
                                 pagination=pagination,
                                 config=config)


@app.route('/tag/<tag>')
@admin_only
def search_all_tags(tag):
    """Load entries with a tag within all notebooks."""

    # Defaults and parameters
    type = request.args.get('type') or 'html'
    sortby = request.args.get('sort') or config.default_search_order
    page = int(request.args.get('page') or 1)

    # Data
    tags = tag.split(' ')
    query = " ".join(["#" + t for t in tags])
    search_query = " ".join(["tag:" + t for t in tags])
    db_entries, total_hits, total_pages = vinci.search(search_query,
                                                       page,
                                                       sortby)
    entries = utils.entries.process_entries(db_entries)

    base_url = '%stag/%s' % (url_for('index'), tag)
    pagination = utils.pagination.get_pagination(page,
                                                 total_hits,
                                                 total_pages,
                                                 sortby,
                                                 base_url)

    return utils.template.render('list',
                                 type,
                                 title="Search All Tags",
                                 query=query,
                                 entries=entries,
                                 pagination=pagination,
                                 config=config)


# Search within a notebook
@app.route('/<notebook_slug>/search/<query>')
@notebook_access
def search_notebook(notebook_slug, query):
    """Search within a notebook"""

    # Defaults and parameters
    type = request.args.get('type', 'html')
    sortby = request.args.get('sort', config.default_search_order)
    page = int(request.args.get('page', 1))

    # Data
    notebook = vinci.get_notebook(notebook_slug)
    original_query = query
    display_query = re.sub(r'tag:', '#', original_query)
    search_query = original_query + ' notebook:' + notebook_slug
    query = re.sub(r'tag:', '#', search_query)
    db_entries, total_hits, total_pages = vinci.search(query, page, sortby)
    entries = utils.entries.process_entries(db_entries)

    base_url = '{0}{1}/search/{2}'.format(url_for('index'),
                                          notebook_slug,
                                          original_query)
    pagination = utils.pagination.get_pagination(page,
                                                 total_hits,
                                                 total_pages,
                                                 sortby,
                                                 base_url)

    return utils.template.render('list',
                                 type,
                                 title=notebook.name,
                                 notebook=notebook,
                                 query=display_query,
                                 entries=entries,
                                 pagination=pagination,
                                 config=config)


@app.route('/<notebook_slug>/tag/<tag>')
@notebook_access
def search_tags_in_notebook(notebook_slug, tag):
    """Load entries with a tag within a notebook."""

    # Defaults and parameters
    type = request.args.get('type') or 'html'
    sortby = request.args.get('sort') or config.default_search_order
    page = int(request.args.get('page') or 1)

    # Data
    notebook = vinci.get_notebook(notebook_slug)
    tags = tag.split(' ')
    query = " ".join(["#" + t for t in tags])
    notebook_query = 'notebook:' + notebook_slug
    search_query = " ".join(["tag:" + t for t in tags])
    search_query += ' ' + notebook_query
    db_entries, total_hits, total_pages = vinci.search(search_query,
                                                       page,
                                                       sortby)
    entries = utils.entries.process_entries(db_entries)

    base_url = '{0}{1}/tag/{2}'.format(url_for('index'),
                                       notebook_slug,
                                       tag)
    pagination = utils.pagination.get_pagination(page,
                                                 total_hits,
                                                 total_pages,
                                                 sortby,
                                                 base_url)

    return utils.template.render('list',
                                 type,
                                 title=notebook.name,
                                 notebook=notebook,
                                 query=query,
                                 entries=entries,
                                 pagination=pagination,
                                 config=config)


@app.route('/<notebook_slug>/entry/<entry_id>')
@notebook_access
def display_entry(notebook_slug, entry_id):
    """Display a single entry."""

    # Defaults and parameters
    type = request.args.get('type') or 'html'

    if re.match(r'^\d{4}-\d{2}-\d{2}\.\d+$', entry_id):
        # Parse the entry ID out
        id = entry_id[entry_id.find('.') + 1:]
        db_entry = vinci.get_entry(notebook_slug, id=id)
    else:
        try:
            db_entry = vinci.get_entry(notebook_slug, slug=entry_id)
        except Entry.DoesNotExist:
            content = unicode("\n".join(['slug:' + entry_id,
                                         '----',
                                         'No content']))
            db_entry = vinci.add_entry(content, notebook_slug, slug=entry_id)

    # Data
    notebook = vinci.get_notebook(notebook_slug)
    entry = utils.entries.process_entry(db_entry)

    return utils.template.render('entry',
                                 type,
                                 notebook=notebook,
                                 title=notebook.name,
                                 entry=entry,
                                 config=config)


@app.route('/<notebook_slug>/')
@notebook_access
def display_entries(notebook_slug):
    """Display entries for a notebook."""

    # Defaults and parameters
    type = request.args.get('type') or 'html'
    sortby = request.args.get('sort') or config.default_search_order
    page = int(request.args.get('page') or 1)

    # Data
    notebook = vinci.get_notebook(notebook_slug)
    results_per_page = config.results_per_page
    (db_entries, total_hits, total_pages) = vinci.get_entries(notebook_slug,
                                                              sortby,
                                                              page,
                                                              results_per_page)
    entries = utils.entries.process_entries(db_entries)

    base_url = '%s%s' % (url_for('index'), notebook_slug)
    pagination = utils.pagination.get_pagination(page,
                                                 total_hits,
                                                 total_pages,
                                                 sortby,
                                                 base_url)

    return utils.template.render('list',
                                 type,
                                 notebook=notebook,
                                 title=notebook.name,
                                 entries=entries,
                                 pagination=pagination,
                                 config=config)


@app.route('/')
@admin_only
def index():
    """Home page."""
    # Defaults and parameters
    type = request.args.get('type') or 'html'

    notebooks = vinci.get_all_notebooks()

    return utils.template.render('index',
                                 type,
                                 title="All Notebooks",
                                 notebooks=notebooks)


# 404
@app.errorhandler(404)
def page_not_found(error):
    return utils.template.render('404', 'html', title='File Not Found'), 404


# 500
@app.errorhandler(500)
def server_error(error):
    return utils.template.render('500',
                                 'html',
                                 title='Something crashed.',
                                 error=error), 500


if __name__ == '__main__':
    app.debug = config.debug
    app.run()
