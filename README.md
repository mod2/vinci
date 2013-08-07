## Vinci

Web-based notebook.

### Installation

1. Create a virtualenv (we recommend virtualenvwrapper).
2. Activate your virtualenv.
3. Run `pip install -r requirements.txt`.
4. Copy `config_sample.py` to `config.py` and edit.

### Plugins

Plugins come in two parts: a Python preprocessor (located in `plugins/[pluginname].py`) and a JavaScript postprocessor (located in `static/plugins/[pluginname]/[pluginname].js`). See examples.

To activate a plugin, add it to the `plugins` entry in `config.py`. Make sure you add any CSS/JS files the plugin needs to include.

### Keyboard shortcuts

* `j`/`k` in entry list
* `n` to go to the notebook page
* `h` to go to notebook/entry/home
* `a` to go to the all notebooks page
