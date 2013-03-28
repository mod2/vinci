# Vinci web app

from flask import Flask, request, render_template
from flask import url_for, send_from_directory, jsonify, redirect
from flaskext.markdown import Markdown
from markdown import markdown
from smartypants import smartyPants
from datetime import datetime
import os
import re
import logging

import config
import vinci
import utils.filters

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

# Set up Jinja2 filters for Markdown and hashtags
Markdown(app)
app.jinja_env.filters['hashtag'] = utils.filters.hashtag


# Favicon
@app.route('/favicon.ico/')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


# Add an entry
@app.route('/add/entry/')
def add_entry():
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
        html = utils.filters.convert_hashtags(content,
                                              url_for('index'),
                                              notebook,
                                              '/tag')
        html = smartyPants(markdown(html))

        # Send the info we need to generate the entry HTML
        response = {
            'status': 'success',
            'id': entry.id,
            'url': '%s.%s' % (entry.date.strftime('%Y-%m-%d'), entry.id),
            'date': entry.date.strftime('%a, %d %b %Y'),
            'time': entry.date.strftime('%l:%M %p').strip(),
            'html': html
        }

        return response_with_callback(response, callback)
    else:
        response = {'status': 'error'}

        return jsonify(response)


# Delete an entry
@app.route('/delete/entry/')
def delete_entry():
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


# Edit an entry
# TODO: refactor this, lots of shared code with add_entry()
@app.route('/edit/entry/')
def edit_entry():
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
        html = utils.filters.convert_hashtags(content,
                                              url_for('index'),
                                              notebook,
                                              '/tag')
        html = smartyPants(markdown(html))

        # Send the info we need to generate the entry HTML
        response = {
            'status': 'success',
            'id': entry.id,
            'url': '%s.%s' % (entry.date.strftime('%Y-%m-%d'), entry.id),
            'date': entry.date.strftime('%a, %d %b %Y'),
            'time': entry.date.strftime('%l:%M %p').strip(),
            'html': html
        }

        return response_with_callback(response, callback)
    else:
        response = {'status': 'error'}

        return jsonify(response)


# Add a notebook
@app.route('/add/notebook/')
def add_notebook():
    # Defaults and parameters
    name = request.args.get('name')
    description = request.args.get('desc')
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


# Delete a notebook
@app.route('/delete/notebook/')
def delete_notebook():
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


# Rename a notebook
@app.route('/rename/notebook/')
def edit_notebook():
    # Defaults and parameters
    notebook = request.args.get('notebook')
    name = request.args.get('name')
    callback = request.args.get('callback')
    #type = request.args.get('type') or 'json'

    # Edit the entry
    notebook = vinci.rename_notebook(notebook_slug=notebook, name=name)

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
    """ Search within all notebooks"""

    # Defaults and parameters
    type = request.args.get('type') or 'html'

    # Template to load
    template = 'list.%s' % type

    # Data
    entries = vinci.search(query)

    return render_template(template,
                           title="Search All Notebooks",
                           query=query,
                           entries=entries)


@app.route('/tag/<tag>')
def search_all_tags(tag):
    """ Load entries with a tag within all notebooks """

    # Defaults and parameters
    type = request.args.get('type') or 'html'

    # Template to load
    template = 'list.%s' % type

    # Data
    tags = tag.split(' ')
    query = " ".join(["#" + t for t in tags])
    search_query = " ".join(["tag:" + t for t in tags])
    entries = vinci.search(search_query)

    return render_template(template,
                           title="Search All Tags",
                           query=query,
                           entries=entries)


# Search within a notebook
@app.route('/<notebook_slug>/search/<query>')
def search_notebook(notebook_slug, query):
    """Search within a notebook"""

    # Defaults and parameters
    type = request.args.get('type') or 'html'

    # Template to load
    template = 'list.%s' % type

    # Data
    notebook = vinci.get_notebook(notebook_slug)
    search_query = query + ' notebook:' + notebook_slug
    query = re.sub(r'tag:', '#', query)
    entries = vinci.search(search_query)

    return render_template(template,
                           title=notebook.name,
                           query=query,
                           notebook=notebook,
                           entries=entries)


@app.route('/<notebook_slug>/tag/<tag>')
def search_tags_in_notebook(notebook_slug, tag):
    """ Load entries with a tag within a notebook """

    # Defaults and parameters
    type = request.args.get('type') or 'html'

    # Template to load
    template = 'list.%s' % type

    # Data
    notebook = vinci.get_notebook(notebook_slug)
    tags = tag.split(' ')
    query = " ".join(["#" + t for t in tags])
    search_query = " ".join(["tag:" + t for t in tags]) + ' notebook:' + notebook_slug
    entries = vinci.search(search_query)

    return render_template(template,
                           title=notebook.name,
                           query=query,
                           notebook=notebook,
                           entries=entries)


# Display a single entry
@app.route('/<notebook_slug>/entry/<entry_id>')
def display_entry(notebook_slug, entry_id):
    # Defaults and parameters
    type = request.args.get('type') or 'html'

    # Template to load
    template = 'entry.%s' % type

    # Parse the entry ID out
    id = entry_id[entry_id.find('.')+1:]

    # Data
    notebook = vinci.get_notebook(notebook_slug)
    entry = vinci.get_entry(id, notebook_slug)

    return render_template(template,
                           title=notebook.name,
                           notebook=notebook,
                           entry=entry)


@app.route('/<notebook_slug>/')
def display_entries(notebook_slug):
    # Defaults and parameters
    type = request.args.get('type') or 'html'

    # Template to load
    template = 'list.%s' % type

    # Data
    notebook = vinci.get_notebook(notebook_slug)
    entries = vinci.get_entries(notebook_slug)

    return render_template(template,
                           title=notebook.name,
                           notebook=notebook,
                           entries=entries)


# Home page
@app.route('/')
def index():
    # Defaults and parameters
    type = request.args.get('type') or 'html'

    # Template to load
    template = 'index.%s' % type

    notebooks = vinci.get_all_notebooks()

    return render_template(template,
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
