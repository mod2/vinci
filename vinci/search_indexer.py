import config
import os
import os.path
import re
import math
import whoosh.index as index
from whoosh.fields import Schema, TEXT, KEYWORD, ID, DATETIME
from whoosh import highlight
from whoosh.analysis import StemmingAnalyzer
from whoosh.qparser import QueryParser
from whoosh.qparser.dateparse import DateParserPlugin
from models import Entry, init_db


def get_or_create_index():
    """Returns an index object. Create it if it doesn't exist."""
    if not os.path.exists(config.index_dir):
        os.mkdir(config.index_dir)
        return full_index()

    if index.exists_in(config.index_dir):
        return index.open_dir(config.index_dir)


def default_index_schema():
    return Schema(id=ID(unique=True, stored=True),
                  notebook=ID,
                  content=TEXT(analyzer=StemmingAnalyzer(), stored=True),
                  tag=KEYWORD(field_boost=2.0),
                  type=ID,
                  date=DATETIME)


def full_index(database_file=config.database_file, admin=config.admin):
    """Create a fresh new index."""
    init_db(database_file, admin)
    ix = index.create_in(config.index_dir, default_index_schema())
    writer = ix.writer()
    for entry in Entry.select():
        etype = u'page' if entry.current_revision.slug != '' else u'entry'
        writer.add_document(id=unicode(entry.id),
                            notebook=entry.notebook.slug,
                            content=entry.current_revision.content,
                            tag=u" ".join(_get_tags(entry)),
                            type=etype,
                            date=entry.date)
    writer.commit()


def add_or_update_index(document, new=False):
    """Adds or updates the document in the index."""
    ix = get_or_create_index()
    writer = ix.writer()
    etype = u'page' if document.current_revision.slug != '' else u'entry'
    if new:
        writer.add_document(id=unicode(document.id),
                            notebook=document.notebook.slug,
                            content=document.current_revision.content,
                            tag=u" ".join(_get_tags(document)),
                            type=etype,
                            date=document.date)
    else:
        writer.update_document(id=unicode(document.id),
                               notebook=document.notebook.slug,
                               content=document.current_revision.content,
                               tag=u" ".join(_get_tags(document)),
                               type=etype,
                               date=document.date)

    writer.commit()


def delete_from_index(document):
    """Remove a document from the index."""
    ix = get_or_create_index()
    writer = ix.writer()
    writer.delete_by_term(id, unicode(document.id))
    writer.commit()


def _get_tags(entry):
    """Parses the entry content and returns a list of tags found in it."""
    tag_re = re.compile(r"\s#(\w+)")
    other_tags_re = re.compile(r"^tags:(.*)")
    tags = tag_re.findall(entry.current_revision.content)
    header = entry.current_revision.content.split('----')[0]
    if header != '':
        other_tags = other_tags_re.findall(header)
        if len(other_tags) > 0:
            tags.extend(other_tags[0].split(','))
    return tags


def search(query_string, page=1, results_per_page=10, sort_order='relevance'):
    if isinstance(query_string, str):
        query_string = unicode(query_string)

    ix = get_or_create_index()

    qp = QueryParser('content', ix.schema)
    qp.add_plugin(DateParserPlugin(free=True))
    query = qp.parse(query_string)

    entry_ids = {}
    results = None
    frag = highlight.ContextFragmenter(maxchars=300, surround=100)
    hi = highlight.Highlighter(fragmenter=frag)

    with ix.searcher() as searcher:
        if sort_order == 'date_desc':
            results = searcher.search_page(query,
                                           page,
                                           pagelen=results_per_page,
                                           sortedby='date',
                                           reverse=True)
        elif sort_order == 'date_asc':
            results = searcher.search_page(query,
                                           page,
                                           pagelen=results_per_page,
                                           sortedby='date')
        else:
            results = searcher.search_page(query,
                                           page,
                                           pagelen=results_per_page)
        entry_ids = {int(entry['id']): (entry.rank, hi.highlight_hit(entry,
                                                                     'content'))
                     for entry in results}

    return (entry_ids,
            len(results),
            math.ceil(len(results) / float(results_per_page)))
