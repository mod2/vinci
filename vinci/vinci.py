import vinci.models as m
import vinci.utils as utils
import config


def database_required(fn):
    def wrapped():
        m.init_db(config.database_file)
        return fn()
    return wrapped


@database_required
def createNotebook(name, description=None):
    """Create a new Notebook."""
    nb = m.Notebook(name=name, description=description)
    nb.slug = utils.slugify(nb.name)
    nb.save()
