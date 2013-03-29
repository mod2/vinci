# Pagination functions

import config

def get_pagination(page, total_hits, total_pages, sortby, base_url):
    """ Return pagination object for template use """

    # Make sure these things are integers
    page = int(page) or 1
    total_hits = int(total_hits) or 0
    total_pages = int(total_pages) or 0

    pagination = { }
    pagination['page'] = int(page)
    pagination['hits'] = total_hits
    pagination['pages'] = total_pages
    pagination['sort'] = sortby
    pagination['has_prev'] = page > 1
    pagination['has_next'] = page < total_pages

    query_string = { }
    if sortby != config.default_search_order:
        query_string['sort'] = sortby

    if pagination['has_prev']:
        query_string['page'] = page - 1
        pagination['prev_page'] = '%s?%s' % (base_url, '&'.join(['%s=%s' % (key, value) for key, value in query_string.items()]))

    if pagination['has_next']:
        query_string['page'] = page + 1
        pagination['next_page'] = '%s?%s' % (base_url, '&'.join(['%s=%s' % (key, value) for key, value in query_string.items()]))

    return pagination
