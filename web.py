# Vinci web app

from flask import Flask, request, render_template, url_for, send_from_directory
import config
import os
import vinci

app = Flask(__name__)

@app.route('/favicon.ico/')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/<notebook_slug>/')
@app.route('/<notebook_slug>/type:<response_type>/')
def display_entries(notebook_slug, response_type='html'):
    # Choose template (TODO: refactor)
    if response_type == 'html':
        template = 'list.html'
    elif response_type == 'json':
        template = 'list-json.html'

    notebook = vinci.get_notebook(notebook_slug)
    entries = vinci.get_entries(notebook_slug)

    return render_template(template, notebook=notebook, entries=entries)

@app.route('/<notebook_slug>/add')
def add_entry(notebook_slug):
    content = request.args.get('content')
    date = request.args.get('date')

    if vinci.add_entry(content=content, notebook_slug=notebook_slug, date=date):
        return '1'
    else:
        return '0'

@app.route('/')
def index():
    return 'hello'

#@app.route('/<notebook>/<entry_id>')
#@app.route('/search/<query>')
#@app.route('/<notebook>/search/<query>')

if __name__ == '__main__':
    app.debug = config.debug
    app.run()
