from flask import request, g, redirect, url_for
from functools import wraps
import config


#Authentication and Authentication Decorators
def logged_in(func):
    """Decorator to make sure that a user is logged in.
    Users will not be able to access the functionality in the
    wrapped function until they have successfully logged in.
    Redirects is not logged in."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper


def admin_only(func):
    """Decorator to make sure the authenticated user is an admin.
    Users will not be able to access the functionality in the
    wrapped function until they have successfully logged in and
    are a valid admin user.
    Redirects if not admin."""
    @wraps(func)
    @logged_in
    def wrapper(*args, **kwargs):
        if g.user.admin is False:
            return redirect(url_for('no_permission'))
        return func(*args, **kwargs)
    return wrapper


def notebook_access(func):
    """Decorator to make sure the authenticated user has permission
    to access the notebook.
    Users will not be able to access the functionality in the
    wrapped function until they have successfully logged in
    and have sufficient permissions.
    Redirects is user doesn't have permission."""
    @wraps(func)
    @logged_in
    def wrapper(*args, **kwargs):
        notebook = str(kwargs['notebook_slug'])
        username = str(g.user.username)
        notebook_access = []
        if notebook in config.notebook_access.keys():
            notebook_access = config.notebook_access[notebook]
        if g.user.admin is False and username not in notebook_access:
            return redirect(url_for('no_permission'))
        return func(*args, **kwargs)
    return wrapper


def ws_access(func):
    """Decorator to lock down access to web service calls."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if g.user is None and request.args.get('key', '') != config.ws_key:
            return redirect(url_for('no_permission'))
        return func(*args, **kwargs)
    return wrapper
