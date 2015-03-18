from django.conf import settings
from django.http.response import HttpResponseNotFound
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from vinci.models import Notebook, Entry


def entries_list(request, notebook_slug):
    sortby = request.GET.get('sort', settings.VINCI_DEFAULT_SEARCH_ORDER)
    page = int(request.GET.get('page', 1))

    notebook = get_object_or_404(Notebook, slug=notebook_slug)
    entries = notebook.entries.all().order_by(sortby)
    context = {
        'title': notebook.name,
        'notebook': notebook,
        'entries': (Paginator(entries, settings.VINCI_RESULTS_PER_PAGE)
                    .page(page)),
    }

    return render_to_response('vinci/list.html',
                              context,
                              RequestContext(request),
                              )


def entry_detail(request, notebook_slug, entry_slug):
    try:
        entry = Entry.objects.get(Q(notebook__slug=notebook_slug)
                                  & (Q(id=int(entry_slug))
                                     | Q(slug=entry_slug)))
    except Entry.DoesNotExist:
        return HttpResponseNotFound('Entry does not exist.')
    context = {
        'title': entry.notebook.name,
        'entry': entry,
    }
    return render_to_response('vinci/entry.html',
                              context,
                              RequestContext(request),
                              )


def notebooks_list(request):
    notebooks = Notebook.objects.all()
    context = {
        'title': 'All Notebooks',
        'notebooks': notebooks,
    }

    return render_to_response('vinci/index.html',
                              context,
                              RequestContext(request),
                              )
