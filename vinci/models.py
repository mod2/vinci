from datetime import datetime
import vinci.utils as utils
import peewee as p
import json

db = p.SqliteDatabase(None, threadlocals=True)
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class BaseModel(p.Model):
    class Meta:
        database = db


class Notebook(BaseModel):
    slug = p.CharField(max_length=100, unique=True)
    name = p.CharField(max_length=100)
    description = p.TextField(null=True)

    def set_slug(self):
        slug = utils.slugify(self.name)
        num = Notebook.select().where(
                p.fn.Substr(Notebook.slug, 1, len(slug)) == slug).count()
        if num > 0:
            slug += '-' + str(num)
        self.slug = slug


class User(BaseModel):
    username = p.CharField(max_length=100, unique=True)
    display = p.CharField(max_length=50, unique=True)
    admin = p.BooleanField(default=False)


class Entry(BaseModel):
    content = p.TextField()
    notebook = p.ForeignKeyField(Notebook, related_name='entries')
    author = p.ForeignKeyField(User, related_name='entries')
    date = p.DateTimeField(default=datetime.now)
    last_modified = p.DateTimeField(default=datetime.now)

    class Meta:
        order_by = ('-date',)

    def save(self, force_insert=False, only=None):
        try:
            if self.author is not None:
                pass
        except p.DoesNotExist:
            self.author = User.get(User.id == 1)
        self.last_modified = datetime.now()
        return super(Entry, self).save(force_insert, only)

    def serializable(self):
        entry = {}
        entry['content'] = self.content
        entry['notebook'] = self.notebook.slug
        entry['author'] = self.author.display
        entry['date'] = self.date.strftime(DATETIME_FORMAT)
        entry['last_modified'] = self.last_modified.strftime(DATETIME_FORMAT)
        return entry


def init_db(dbname, admin):
    db.init(dbname)
    Notebook.create_table(True)
    Entry.create_table(True)
    User.create_table(True)
    # add the admin user if doesn't exist
    if User.select().count() == 0:
        admin = User(username=admin['username'],
                     display=admin['display'],
                     admin=True)
        admin.save()
