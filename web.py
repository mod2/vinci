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

logger = logging.getLogger('simple_example')
logger.setLevel(logging.INFO)

fh = logging.FileHandler('/srv/www/logs/vinci-py.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

app = Flask(__name__)

# Set up Jinja2 filters for Markdown and hashtags
Markdown(app)
app.jinja_env.filters['hashtag'] = jinja_filters.hashtag

logger.info('routing favicon')
@app.route('/favicon.ico/')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

logger.info('routing add entry')
# Add an entry
@app.route('/add/entry/')
def add_entry():
    # Defaults
    type = 'json'

    # Load params
    notebook = request.args.get('notebook')
    content = request.args.get('content')
    date = request.args.get('date')
    callback = request.args.get('callback')
    type = request.args.get('type')

    entry = vinci.add_entry(content=content, notebook_slug=notebook, date=date)

    # If we succeeded
    if entry:
        if date == None:
            date = entry.date   # TODO: fix

        # Send the info we need to generate the entry HTML
        response = {
            'status': 'success',
            'id': entry.id, # TODO: fix
            'url': '%s.%s' % (date.strftime('%Y-%m-%d'), entry.id), # TODO: fix
            'date': date.strftime('%a, %d %b %Y'), # TODO: fix
            'time': date.strftime('%l:%M %p').strip(), # TODO: fix
            'html': smartyPants(markdown(content))
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

logger.info('routing delete entry')
# Delete an entry
@app.route('/delete/entry/')
def delete_entry():
    # Defaults
    type = 'json'

    # Load params
    notebook = request.args.get('notebook')
    id = request.args.get('id')
    callback = request.args.get('callback')
    type = request.args.get('type')

logger.info('routing edit entry')
# Edit an entry
@app.route('/edit/entry/')
def edit_entry():
    # Defaults
    type = 'json'

    # Load params
    notebook = request.args.get('notebook')
    id = request.args.get('id')
    content = request.args.get('content')
    callback = request.args.get('callback')
    type = request.args.get('type')

logger.info('routing add notebook')
# Add a notebook
@app.route('/add/notebook/')
def add_notebook():
    # Defaults
    type = 'json'

    # Load params
    name = request.args.get('name')
    callback = request.args.get('callback')
    type = request.args.get('type')

logger.info('routing delete notebook')
# Delete a notebook
@app.route('/delete/notebook/')
def delete_notebook():
    # Defaults
    type = 'json'

    # Load params
    notebook = request.args.get('notebook')
    callback = request.args.get('callback')
    type = request.args.get('type')

logger.info('routing edit notebook')
# Edit (rename) a notebook
@app.route('/edit/notebook/')
def edit_notebook():
    # Defaults
    type = 'json'

    # Load params
    notebook = request.args.get('notebook')
    name = request.args.get('name')
    callback = request.args.get('callback')
    type = request.args.get('type')

logger.info('routing search all notebook')
# Search within all notebooks
@app.route('/search/<query>')
def search_all_notebooks(query):
    # Defaults
    type = 'html'

    # Load params
    type = request.args.get('type')

logger.info('routing tag')
# Load entries with a tag within all notebooks
@app.route('/tag/<tag>')
def search_all_tags(tag):
    # Defaults
    type = 'html'

    # Load params
    type = request.args.get('type')

logger.info('routing notebook search')
# Search within a notebook
@app.route('/<notebook_slug>/search/<query>')
def search_notebook(notebook_slug, query):
    # Defaults
    type = 'html'

    # Load params
    type = request.args.get('type')

logger.info('routing notebook tag')
# Load entries with a tag within a notebook
@app.route('/<notebook_slug>/tag/<tag>')
def search_tags_in_notebook(notebook_slug, tag):
    # Defaults
    type = 'html'

    # Load params
    type = request.args.get('type')

logger.info('routing entry')
# Display a single entry
@app.route('/<notebook_slug>/entry/<entry_id>')
def display_entry(notebook_slug, entry_id):
    # Defaults
    type = 'html'

    # Load params
    type = request.args.get('type')

logger.info('routing entries')
@app.route('/<notebook_slug>/')
def display_entries(notebook_slug):
    # Defaults
    type = request.args.get('type') or 'html'
    logger.info('type: %s' % type)

    # Template to load
    template = 'list.%s' % type
    logger.info('template: %s, %s' % (template, notebook_slug))

    # Data
    notebook = vinci.get_notebook(notebook_slug)
    entries = vinci.get_entries(notebook_slug)
    logger.info('loaded data')

    return render_template(template, notebook=notebook, entries=entries)

# Home page
@app.route('/')
def index():
    return 'hello'


if __name__ == '__main__':
    app.debug = config.debug
    app.run()
