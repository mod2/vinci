## Vinci

A web-based notebook app written in Django. Tested with Python 3.x.

### Installation

These installation instructions assume some basic knowledge of Django.

- Clone the repo
- Create a virtualenv for the project if you want
- Copy `local_settings_sample.py` to `local_settings.py` and edit to taste (and make sure you put something in `SECRET_KEY`)
- `pip install -r requirements.txt`
- `./manage.py migrate`
- `./manage.py createsuperuser`
- `./manage.py runserver 8001`

### Plugins

**needs to be updated**

Plugins come in two parts: a Python preprocessor (located in `plugins/[pluginname].py`) and a JavaScript postprocessor (located in `static/plugins/[pluginname]/[pluginname].js`). See examples.

To activate a plugin, add it to the `plugins` entry in `config.py`. Make sure you add any CSS/JS files the plugin needs to include.

### Keyboard shortcuts

- `?` to see list of keyboard shortcuts
