# Vinci web app

from flask import Flask, request, render_template, url_for, send_from_directory, jsonify, redirect
from datetime import datetime
import os
import re
import logging

import config
import vinci
import utils.text
import utils.entries
import utils.pagination
import utils.template
import plugins

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

# Initialize the Flask app
app = Flask(__name__)
config.root_path = app.root_path

# Initialize database
vinci.init_db()


@app.route('/favicon.ico/')
def favicon():
    """Serve up the favicon."""
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/add/entry/')
def add_entry():
    """Add an entry."""
    # Defaults and parameters
    notebook = request.args.get('notebook')
    content = request.args.get('content')
    date = request.args.get('date')
    callback = request.args.get('callback')
    #type = request.args.get('type') or 'json'

    # If the date is a string, convert it to datetime first
    if date and isinstance(date, unicode):
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    elif date and isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

    # Add the entry
    entry = vinci.add_entry(content=content, notebook_slug=notebook, date=date)

    # If we succeeded
    if entry:
        # Prep the HTML
        html, plugins = utils.text.process(content,
                                           '%s%s' % (url_for('index'), notebook))

        # Send the info we need to generate the entry HTML
        response = {
            'status': 'success',
            'id': entry.id,
            'url': '%s.%s' % (entry.date.strftime('%Y-%m-%d'), entry.id),
            'date': entry.date.strftime('%a, %d %b %Y'),
            'time': entry.date.strftime('%l:%M %p').strip(),
            'datetime': entry.date.strftime('%Y-%m-%d %H:%M:%S'),
            'html': html,
            'content': content,
            'plugins': plugins,
        }

        return response_with_callback(response, callback)
    else:
        response = {'status': 'error'}

        return jsonify(response)


@app.route('/delete/entry/')
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
@app.route('/edit/entry/')
def edit_entry():
    """Edit an entry."""

    # Defaults and parameters
    notebook = request.args.get('notebook')
    id = request.args.get('id')
    content = request.args.get('content')
    date = request.args.get('date')
    callback = request.args.get('callback')
    #type = request.args.get('type') or 'json'

    # Edit the entry
    entry = vinci.edit_entry(id=id,
                             content=content,
                             notebook_slug=notebook,
                             date=date)

    # If we succeeded
    if entry:
        # Prep the HTML
        html, plugins = utils.text.process(content,
                                           '%s%s' % (url_for('index'), notebook))

        # Send the info we need to generate the entry HTML
        response = {
            'status': 'success',
            'id': entry.id,
            'url': '%s.%s' % (entry.date.strftime('%Y-%m-%d'), entry.id),
            'date': entry.date.strftime('%a, %d %b %Y'),
            'time': entry.date.strftime('%l:%M %p').strip(),
            'datetime': entry.date.strftime('%Y-%m-%d %H:%M:%S'),
            'html': html,
            'content': content,
            'plugins': plugins,
        }

        return response_with_callback(response, callback)
    else:
        response = {'status': 'error'}

        return jsonify(response)


@app.route('/add/notebook/')
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
def edit_notebook():
    """Edit a notebook."""

    # Defaults and parameters
    notebook = request.args.get('notebook')
    name = request.args.get('name')
    description = request.args.get('description')
    callback = request.args.get('callback')
    #type = request.args.get('type') or 'json'

    # Edit the entry
    notebook = vinci.edit_notebook(notebook_slug=notebook, name=name, description=description)

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
def reindex():
    """Reindex the index."""

    vinci.reindex()
    return redirect(url_for('index'))


@app.route('/search/<query>')
def search_all_notebooks(query):
    """Search within all notebooks."""

    # Defaults and parameters
    type = request.args.get('type') or 'html'
    sortby = request.args.get('sort') or config.default_search_order
    page = int(request.args.get('page') or 1)

    # Data
    db_entries, total_hits, total_pages = vinci.search(query, page, sortby)
    entries = utils.entries.process_entries(db_entries)

    base_url = '%ssearch/%s' % (url_for('index'), query) 
    pagination = utils.pagination.get_pagination(page, total_hits, total_pages, sortby, base_url)

    return utils.template.render('list',
                                 type,
                                 title="Search All Notebooks",
                                 query=query,
                                 entries=entries,
                                 pagination=pagination)


@app.route('/tag/<tag>')
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
    db_entries, total_hits, total_pages = vinci.search(search_query, page, sortby)
    entries = utils.entries.process_entries(db_entries)

    base_url = '%stag/%s' % (url_for('index'), tag) 
    pagination = utils.pagination.get_pagination(page, total_hits, total_pages, sortby, base_url)

    return utils.template.render('list',
                                 type,
                                 title="Search All Tags",
                                 query=query,
                                 entries=entries,
                                 pagination=pagination)


# Search within a notebook
@app.route('/<notebook_slug>/search/<query>')
def search_notebook(notebook_slug, query):
    """Search within a notebook"""

    # Defaults and parameters
    type = request.args.get('type') or 'html'
    sortby = request.args.get('sort') or config.default_search_order
    page = int(request.args.get('page') or 1)

    # Data
    notebook = vinci.get_notebook(notebook_slug)
    original_query = query
    search_query = original_query + ' notebook:' + notebook_slug
    query = re.sub(r'tag:', '#', search_query)
    db_entries, total_hits, total_pages = vinci.search(query, page, sortby)
    entries = utils.entries.process_entries(db_entries)

    base_url = '%s%s/search/%s' % (url_for('index'), notebook_slug, original_query) 
    pagination = utils.pagination.get_pagination(page, total_hits, total_pages, sortby, base_url)

    return utils.template.render('list',
                                 type,
                                 title=notebook.name,
                                 notebook=notebook,
                                 query=query,
                                 entries=entries,
                                 pagination=pagination)


@app.route('/<notebook_slug>/tag/<tag>')
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
    search_query = " ".join(["tag:" + t for t in tags]) + ' notebook:' + notebook_slug
    db_entries, total_hits, total_pages = vinci.search(search_query, page, sortby)
    entries = utils.entries.process_entries(db_entries)

    base_url = '%s%s/tag/%s' % (url_for('index'), notebook_slug, tag) 
    pagination = utils.pagination.get_pagination(page, total_hits, total_pages, sortby, base_url)

    return utils.template.render('list',
                                 type,
                                 title=notebook.name,
                                 notebook=notebook,
                                 query=query,
                                 entries=entries,
                                 pagination=pagination)


@app.route('/<notebook_slug>/entry/<entry_id>')
def display_entry(notebook_slug, entry_id):
    """Display a single entry."""

    # Defaults and parameters
    type = request.args.get('type') or 'html'

    # Parse the entry ID out
    id = entry_id[entry_id.find('.')+1:]

    # Data
    notebook = vinci.get_notebook(notebook_slug)
    db_entry = vinci.get_entry(id, notebook_slug)
    entry = utils.entries.process_entry(db_entry)

    return utils.template.render('entry',
                                 type,
                                 notebook=notebook,
                                 title=notebook.name,
                                 entry=entry,
                                 config=config)


@app.route('/<notebook_slug>/')
def display_entries(notebook_slug):
    """Display entries for a notebook."""

    # Defaults and parameters
    type = request.args.get('type') or 'html'
    sortby = request.args.get('sort') or config.default_search_order
    page = int(request.args.get('page') or 1)

    # Data
    notebook = vinci.get_notebook(notebook_slug)
    db_entries, total_hits, total_pages = vinci.get_entries(notebook_slug,
                                                            sortby,
                                                            page,
                                                            config.results_per_page)
    entries = utils.entries.process_entries(db_entries)

    base_url = '%s%s' % (url_for('index'), notebook_slug) 
    pagination = utils.pagination.get_pagination(page, total_hits, total_pages, sortby, base_url)

    return utils.template.render('list',
                                 type,
                                 notebook=notebook,
                                 title=notebook.name,
                                 entries=entries,
                                 pagination=pagination,
                                 config=config)


@app.route('/')
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
    return render_template('404.html', title='File Not Found'), 404


# 500
@app.errorhandler(500)
def server_error(error):
    return render_template('500.html', title='Something crashed.'), 500


# Redirect if callback, otherwise return JSONed response
def response_with_callback(response, callback):
    if callback:
        return redirect(callback)
    else:
        return jsonify(response)


if __name__ == '__main__':
    app.debug = config.debug
    app.run()
