import os
import os.path
import vinci.models as m
import nose.tools as testtools

TEST_DB = '/tmp/testing_db.db'

def setup():
    m.init_db(TEST_DB)

def teardown():
    if os.path.isfile(TEST_DB):
        os.remove(TEST_DB)


def test_notebook_create_save():
    nb = m.Notebook(name='Testing Notebook')
    nb.set_slug()
    nb.save()


def test_entry_create_save():
    nb = m.Notebook(name='Testing Notebook')
    nb.set_slug()
    nb.save()
    e1 = m.Entry(content='blah', notebook=nb)
    e2 = m.Entry(content='blah blah', notebook=nb)
    e3 = m.Entry(content='blah blah blah', notebook=nb)
    e1.save()
    e2.save()
    e3.save()
    count = nb.entries.count()
    assert count == 3, "Not all entries saved: %s (should be 3)" % (count,)
    for entry in nb.entries:
        assert 'blah' in entry.content, "not save correctly: %s" % (entry.id,)


def test_same_notebook_slug():
    nb1 = m.Notebook(name='Same')
    nb1.set_slug()
    nb1.save()
    nb2 = m.Notebook(name='Same')
    nb2.set_slug()
    nb2.save()
    assert nb2.slug == 'same-1'
    assert nb1.slug != nb2.slug
