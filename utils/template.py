# Template rendering

from flask import render_template
import os
import config

def render(template, type, **kwargs):
    # Choose the template
    template = '%s.%s' % (template, type)

    # Check for custom notebook CSS/JS
    if 'notebook' in kwargs:
        custom = {}
        custom_path = os.path.join(config.root_path, 'static/custom')
        if (os.path.exists('%s/css/%s.css' % (custom_path, kwargs['notebook'].slug))):
            custom['css'] = True
        if (os.path.exists('%s/js/%s.js' % (custom_path, kwargs['notebook'].slug))):
            custom['js'] = True
        kwargs['custom'] = custom

    # Pass the arguments along and render the template
    return render_template(template, **kwargs)
