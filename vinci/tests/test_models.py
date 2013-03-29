import os
import os.path
import vinci.models as m
#import nose.tools as testtools

TEST_DB = '/tmp/testing_db.db'
TEST_ADMIN = {'username': 'chadgh+testadmin@gmail.com', 'display': 'test'}


def setup():
    m.init_db(TEST_DB, TEST_ADMIN)


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
    a = m.User.get(m.User.display == TEST_ADMIN['display'])
    e1 = m.Entry(content='blah', notebook=nb, author=a)
    e2 = m.Entry(content='blah blah', notebook=nb, author=a)
    e3 = m.Entry(content='blah blah blah', notebook=nb)
    e1.save()
    e2.save()
    e3.save()
    count = nb.entries.count()
    assert count == 3, "Not all entries saved: %s (should be 3)" % (count,)
    for entry in nb.entries:
        auth_id = entry.author.id
        assert 'blah' in entry.content, "Error: entry.content" % (entry.id,)
        assert auth_id == 1, "Error: author.id(%s)" % (auth_id)


def test_admin_user():
    admin = m.User.get(m.User.id == 1)
    assert admin.username == TEST_ADMIN['username'], "Error: admin.username"
    assert admin.display == TEST_ADMIN['display'], "Error: admin.display"


def test_same_notebook_slug():
    nb1 = m.Notebook(name='Same')
    nb1.set_slug()
    nb1.save()
    nb2 = m.Notebook(name='Same')
    nb2.set_slug()
    nb2.save()
    assert nb2.slug == 'same-1', "Error: notebook.slug(%s" % (nb2.slug)
    assert nb1.slug != nb2.slug, "Error: slugs are equal"
