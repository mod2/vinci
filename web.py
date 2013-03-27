# Vinci web app

from flask import Flask, request, render_template, url_for, send_from_directory, jsonify
from flaskext.markdown import Markdown
from markdown import markdown
from smartypants import smartyPants
import config
import os
import vinci
import logging
import jinja_filters

# Set up some logging stuff
if config.debug:
    logger = logging.getLogger('simple_example')
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler(config.log_file)
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

# Initialize the Flask app
app = Flask(__name__)

# Set up Jinja2 filters for Markdown and hashtags
Markdown(app)
app.jinja_env.filters['hashtag'] = jinja_filters.hashtag

# Favicon
@app.route('/favicon.ico/')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Add an entry
@app.route('/add/entry/')
def add_entry():
    # Defaults and parameters
    notebook = request.args.get('notebook')
    content = request.args.get('content')
    date = request.args.get('date')
    callback = request.args.get('callback')
    type = request.args.get('type') or 'json'

    # Add the entry
    entry = vinci.add_entry(content=content, notebook_slug=notebook, date=date)

    # If we succeeded
    if entry:
        if date == None:
            date = entry.date

        # Prep the HTML
        html = jinja_filters.convert_hashtags(content, url_for('index'), notebook, '/tag')
        html = smartyPants(markdown(html))

        # Send the info we need to generate the entry HTML
        response = {
            'status': 'success',
            'id': entry.id,
            'url': '%s.%s' % (date.strftime('%Y-%m-%d'), entry.id),
            'date': date.strftime('%a, %d %b %Y'),
            'time': date.strftime('%l:%M %p').strip(),
            'html': html
        }

        if callback:
            return ''
        else:
            return jsonify(response)
    else:
        response = {
            'status': 'error'
        }

        return jsonify(response)

# Delete an entry
@app.route('/delete/entry/')
def delete_entry():
    # Defaults and parameters
    notebook = request.args.get('notebook')
    id = request.args.get('id')
    callback = request.args.get('callback')
    type = request.args.get('type') or 'json'

# Edit an entry
@app.route('/edit/entry/')
def edit_entry():
    # Defaults and parameters
    notebook = request.args.get('notebook')
    id = request.args.get('id')
    content = request.args.get('content')
    callback = request.args.get('callback')
    type = request.args.get('type') or 'json'

# Add a notebook
@app.route('/add/notebook/')
def add_notebook():
    # Defaults and parameters
    name = request.args.get('name')
    callback = request.args.get('callback')
    type = request.args.get('type') or 'json'

# Delete a notebook
@app.route('/delete/notebook/')
def delete_notebook():
    # Defaults and parameters
    notebook = request.args.get('notebook')
    callback = request.args.get('callback')
    type = request.args.get('type') or 'json'

# Edit (rename) a notebook
@app.route('/edit/notebook/')
def edit_notebook():
    # Defaults and parameters
    notebook = request.args.get('notebook')
    name = request.args.get('name')
    callback = request.args.get('callback')
    type = request.args.get('type') or 'json'

# Search within all notebooks
@app.route('/search/<query>')
def search_all_notebooks(query):
    # Defaults and parameters
    type = request.args.get('type') or 'html'

# Load entries with a tag within all notebooks
@app.route('/tag/<tag>')
def search_all_tags(tag):
    # Defaults and parameters
    type = request.args.get('type') or 'html'

# Search within a notebook
@app.route('/<notebook_slug>/search/<query>')
def search_notebook(notebook_slug, query):
    # Defaults and parameters
    type = request.args.get('type') or 'html'

# Load entries with a tag within a notebook
@app.route('/<notebook_slug>/tag/<tag>')
def search_tags_in_notebook(notebook_slug, tag):
    # Defaults and parameters
    type = request.args.get('type') or 'html'

# Display a single entry
@app.route('/<notebook_slug>/entry/<entry_id>')
def display_entry(notebook_slug, entry_id):
    # Defaults and parameters
    type = request.args.get('type') or 'html'


@app.route('/<notebook_slug>/')
def display_entries(notebook_slug):
    # Defaults and parameters
    type = request.args.get('type') or 'html'

    # Template to load
    template = 'list.%s' % type

    # Data
    notebook = vinci.get_notebook(notebook_slug)
    entries = vinci.get_entries(notebook_slug)

    return render_template(template, notebook=notebook, entries=entries)

# Home page
@app.route('/')
def index():
    return 'hello'


if __name__ == '__main__':
    app.debug = config.debug
    app.run()
