import config
import os
import os.path
import re
import whoosh.index as index
from whoosh.fields import Schema, TEXT, KEYWORD, ID
from whoosh.analysis import StemmingAnalyzer
from whoosh.qparser import QueryParser
from models import Entry, init_db


def get_or_create_index():
    """Returns an index object. Creats it if is doesn't exist."""
    if not os.path.exists(config.index_dir):
        os.mkdir(config.index_dir)

    if index.exists_in(config.index_dir):
        return index.open_dir(config.index_dir)
    else:
        return full_index()


def default_index_schema():
    return Schema(id=ID(unique=True, stored=True),
                  notebook=ID,
                  content=TEXT(analyzer=StemmingAnalyzer()),
                  tag=KEYWORD(field_boost=2.0))


def full_index(database_file=None):
    """Create a fresh new index."""
    if database_file is None:
        database_file = config.database_file
    init_db(database_file)
    ix = index.create_in(config.index_dir, default_index_schema())
    writer = ix.writer()
    for entry in Entry.select():
        writer.add_document(id=unicode(entry.id),
                            notebook=entry.notebook.slug,
                            content=entry.content,
                            tag=u" ".join(_get_tags(entry)))
    writer.commit()


def add_or_update_index(document):
    """Adds or updates the document in the index."""
    ix = get_or_create_index()
    writer = ix.writer()
    writer.add_document(id=unicode(document.id),
                        notebook=document.notebook.slug,
                        content=document.content,
                        tag=u" ".join(_get_tags(document)))
    writer.commit()


def delete_from_index(document):
    """Remove a document from the index."""
    ix = get_or_create_index()
    writer = ix.writer()
    writer.delete_by_term(id, unicode(document.id))
    writer.commit()


def _get_tags(entry):
    """Parses the entry content and returns a list of tags found in it."""
    tag_re = re.compile(r"#(\w+)")
    return tag_re.findall(entry.content)


def search(query_string, database_file=None):
    if database_file is None:
        database_file = config.database_file
    if isinstance(query_string, str):
        query_string = unicode(query_string)
    ix = get_or_create_index()
    query = QueryParser('content', ix.schema).parse(query_string)
    entry_ids = {}
    with ix.searcher() as searcher:
        results = searcher.search(query)
        entry_ids = {int(entry['id']): entry.score for entry in results}
    init_db(database_file)
    entries = Entry.select().where(Entry.id << entry_ids.keys())
    entries_scores = []
    for entry in entries:
        entries_scores.append((entry_ids[entry.id], entry))
    entries_scores.sort(reverse=True)
    return [entry for score, entry in entries_scores]
