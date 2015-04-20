import os
import os.path
# import re
import math

from django.conf import settings
from whoosh import highlight
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import Schema, TEXT, KEYWORD, ID, DATETIME
from whoosh.qparser import QueryParser
from whoosh.qparser.dateparse import DateParserPlugin
import whoosh.index as index

from .models import Entry


SEARCH_INDEX_DIR = settings.VINCI_SEARCH_INDEX_DIR

if settings.VINCI_SEARCH_SCHEMA:
    SCHEMA = settings.VINCI_SEARCH_SCHEMA
else:
    SCHEMA = Schema(id=ID(unique=True, stored=True),
                    notebook=ID,
                    content=TEXT(analyzer=StemmingAnalyzer(), stored=True),
                    # tag=KEYWORD(field_boost=2.0),
                    type=ID,
                    date=DATETIME,
                    )


def get_or_create_index():
    """Returns an index object. Creates one if it doesn't exist."""
    if not os.path.exists(SEARCH_INDEX_DIR):
        os.mkdir(SEARCH_INDEX_DIR)
        return full_index()

    if index.exists_in(SEARCH_INDEX_DIR):
        return index.open_dir(SEARCH_INDEX_DIR)


def _get_tags(entry):
    """Parses the entry content and returns a list of tags found in it."""
    # tag_re = re.compile(r"\s#(\w+)")
    # other_tags_re = re.compile(r"^tags:(.*)")
    # tags = tag_re.findall(entry.current_revision.content)
    # header = entry.current_revision.content.split('----')[0]
    # if header != '':
    #     other_tags = other_tags_re.findall(header)
    #     if len(other_tags) > 0:
    #         tags.extend(other_tags[0].split(','))
    # return tags


def _generate_entry_document(entry):
    type_ = u'page' if entry.slug != '' else u'entry'
    doc = {}
    doc = {'id': unicode(entry.id),
           'notebook': entry.notebook.slug,
           'content': entry.content,
           # 'tag': u" ".join(_get_tags(entry)),
           'type': type_,
           'date': entry.date,
           }
    return doc


def get_gen_func():
    gen_func = _generate_entry_document
    if settings.VINCI_GENERATE_ENTRY_DOCUMENT_FUNCTION:
        gen_func = settings.VINCI_GENERATE_ENTRY_DOCUMENT_FUNCTION
    return gen_func


def full_index():
    """Create a fresh new index."""
    ix = index.create_in(SEARCH_INDEX_DIR, SCHEMA)
    writer = ix.writer()

    gen_func = get_gen_func()

    for entry in Entry.objects.all():  # TODO: might have to be limited
        doc = gen_func(entry)
        writer.add_document(**doc)
    writer.commit()


def add_or_update_index(document, new=False):
    """Adds or updates the document in the index."""
    ix = get_or_create_index()
    writer = ix.writer()
    gen_func = get_gen_func()
    doc = gen_func(document)
    doc_func = 'add_document' if new else 'update_document'
    getattr(writer, doc_func)(**doc)
    writer.commit()


def delete_from_index(document):
    """Remove a document from the index."""
    ix = get_or_create_index()
    writer = ix.writer()
    writer.delete_by_term(id, unicode(document.id))
    writer.commit()


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
        other_args = {}
        if sort_order == 'date_desc':
            other_args['sortedby'] = 'date'
            other_args['reverse'] = True
        elif sort_order == 'date_asc':
            other_args['sortedby'] = 'date'
        results = searcher.search_page(query,
                                       page,
                                       pagelen=results_per_page,
                                       **other_args)
        entry_ids = {int(entry['id']): (entry.rank, hi.highlight_hit(entry,
                                                                     'content'))
                     for entry in results}

    return (entry_ids,
            len(results),
            math.ceil(len(results) / float(results_per_page)))
