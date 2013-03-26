from datetime import datetime
import peewee as p

db = p.SqliteDatabase(None, threadlocals=True)


class BaseModel(p.Model):
    class Meta:
        database = db


class Notebook(BaseModel):
    slug = p.CharField(max_length=200, unique=True)
    name = p.CharField(max_length=200)
    description = p.TextField(null=True)


class Entry(BaseModel):
    content = p.TextField()
    notebook = p.ForeignKeyField(Notebook, related_name='entries')
    created = p.DateTimeField(default=datetime.now)
    last_modified = p.DateTimeField(default=datetime.now)

    class Meta:
        order_by = ('-created',)

    def save(self, force_insert=False, only=None):
        self.last_modified = datetime.now()
        return super(Entry, self).save(force_insert, only)


def init_db(dbname):
    db.init(dbname)
    Notebook.create_table(True)
    Entry.create_table(True)
