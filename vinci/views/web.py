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

    context = {
        'title': notebook.name,
        'notebook': notebook,
        'entries': entries,
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
    sortby = request.GET.get('sort', settings.VINCI_DEFAULT_SEARCH_ORDER)
    page = int(request.GET.get('page', 1))
    query = request.GET.get('q')

    notebook = get_object_or_404(Notebook, slug=notebook_slug)
    entries, num_results, num_pages = si.search(query, page, sort_order=sortby,
                                                notebook=notebook)
    context = {
        'title': notebook.name,
        'query': query,
        'notebook': notebook,
        'entries': (Paginator(entries, settings.VINCI_RESULTS_PER_PAGE)
                    .page(page)),
    }

    return render_to_response('vinci/list.html',
                              context,
                              RequestContext(request),
                              )
