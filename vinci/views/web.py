from django.conf import settings
from django.http.response import HttpResponseNotFound
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from vinci.models import Notebook, Entry
import vinci.search_indexer as si


@login_required
def entries_list(request, notebook_slug):
    sortby = request.GET.get('sort', settings.VINCI_DEFAULT_SEARCH_ORDER)
    page = int(request.GET.get('page', 1))

    notebook = get_object_or_404(Notebook, slug=notebook_slug)

    entries = notebook.entries.all().order_by(sortby)
    entries = Paginator(entries, settings.VINCI_RESULTS_PER_PAGE).page(page)

    notebooks = Notebook.objects.filter(status='active').order_by('name')

    context = {
        'title': notebook.name,
        'notebook': notebook,
        'notebooks': notebooks,
        'entries': entries,
        'page_type': 'list',
    }

    return render_to_response('vinci/list.html',
                              context,
                              RequestContext(request),
                              )


@login_required
def entry_detail(request, notebook_slug, entry_slug):
    try:
        entry = Entry.objects.from_slug(entry_slug, notebook_slug)
    except Entry.DoesNotExist:
        return HttpResponseNotFound('Entry does not exist.')
    context = {
        'title': entry.notebook.name,
        'notebook': entry.notebook,
        'entry': entry,
        'page_type': 'detail',
    }
    return render_to_response('vinci/entry.html',
                              context,
                              RequestContext(request),
                              )


@login_required
def notebooks_list(request):
    notebooks = Notebook.objects.active()
    context = {
        'title': 'All Notebooks',
        'notebooks': notebooks,
        'page_type': 'all',
    }

    return render_to_response('vinci/index.html',
                              context,
                              RequestContext(request),
                              )


@login_required
def search_notebook(request, notebook_slug):
    notebook = get_object_or_404(Notebook, slug=notebook_slug)
    return _search(request, notebook)


@login_required
def search_all(request):
    return _search(request)


def _search(request, notebook=None):
    sortby = request.GET.get('sort', settings.VINCI_DEFAULT_SEARCH_ORDER)
    page = int(request.GET.get('page', 1))
    query = request.GET.get('q')

    if query is None:
        entries = Paginator([], settings.VINCI_RESULTS_PER_PAGE).page(1)
    else:
        search_params = {
            'query_string': query,
            'page': page,
            'sort_order': sortby,
        }
        if notebook:
            search_params['notebook'] = notebook
        entries, __, __ = si.search(**search_params)
        entries = Paginator(entries, settings.VINCI_RESULTS_PER_PAGE)
        total = entries.count
        entries = entries.page(page)

    context = {
        'title': 'Search results',
        'query': query,
        'entries': entries,
        'total': total,
        'page_type': 'list',
    }

    if notebook:
        context['title'] = notebook.name
        context['notebook'] = notebook

    return render_to_response('vinci/list.html',
                              context,
                              RequestContext(request),
                              )
