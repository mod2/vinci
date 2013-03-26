from flask import Flask, request
app = Flask(__name__)

@app.route('/<notebook_slug>/')
@app.route('/<notebook_slug>/type:<response_type>/')
def display_entries(notebook_slug, response_type='html'):
    return " ".join([notebook_slug, response_type])

@app.route('/<notebook>/add')
def add_entry(notebook_slug):
    content = request.args.get('content')

#@app.route('/<notebook>/<entry_id>')
#@app.route('/search/<query>')
#@app.route('/<notebook>/search/<query>')

if __name__ == '__main__':
    app.debug = True
    app.run()
