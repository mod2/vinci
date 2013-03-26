from datetime import datetime
import vinci.utils as utils
import peewee as p

db = p.SqliteDatabase(None, threadlocals=True)


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


class Entry(BaseModel):
    content = p.TextField()
    notebook = p.ForeignKeyField(Notebook, related_name='entries')
    date = p.DateTimeField(default=datetime.now)
    last_modified = p.DateTimeField(default=datetime.now)

    class Meta:
        order_by = ('-date',)

    def save(self, force_insert=False, only=None):
        self.last_modified = datetime.now()
        return super(Entry, self).save(force_insert, only)


def init_db(dbname):
    db.init(dbname)
    Notebook.create_table(True)
    Entry.create_table(True)
