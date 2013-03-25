import peewee as p
import config

db = p.SqliteDatabase(config.database_file)

class Notebook(p.Model):
    slug = p.CharField()
    name = p.CharField()
    description = p.CharField()

    class Meta:
        database = db


class Entry(p.Model):
    content = p.CharField()
    notebook = p.ForeignKeyField(Notebook, related_name='entries')
    date = p.DateField()
    time = p.TimeField()
    last_modified = p.DateTimeField()

    class Meta:
        database = db

if True: # tables not created
    Notebook.create_table()
    Entry.create_table()
