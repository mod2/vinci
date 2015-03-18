from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from vinci.models import Notebook


def entries_list(request, slug):
    # type_ = request.GET.get('type') or 'html'
    sortby = request.GET.get('sort', settings.VINCI_DEFAULT_SEARCH_ORDER)
    page = int(request.GET.get('page', 1))

    notebook = get_object_or_404(Notebook, slug=slug)
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
