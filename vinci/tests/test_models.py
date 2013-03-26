import vinci.models as m
import nose.tools as testtools


def _setup():
    m.init_db('/tmp/testing_db.db')

def _teardown():
    import os
    os.remove('/tmp/testing_db.db')


@testtools.with_setup(setup=_setup, teardown=_teardown)
def test_notebook_create_save():
    from vinci import utils
    nb = m.Notebook(name='Testing Notebook')
    nb.slug = utils.slugify(nb.name)
    nb.save()
