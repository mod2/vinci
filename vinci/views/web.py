# from django import views
from django.conf import settings
from django.views.generic import View
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from vinci.models import Notebook


def notebook_detail(request, slug):
    notebook = get_object_or_404(Notebook, slug=slug)
    context = {
        'title': notebook.name,
        'notebook': notebook,
        'entries': notebook.entries.all(),
    }

    return render_to_response('vinci/list.html', context, RequestContext(request))


def notebooks_list(request):
    notebooks = Notebook.objects.all()
    context = {
        'title': 'All Notebooks',
        'notebooks': notebooks,
    }

    return render_to_response('vinci/index.html', context, RequestContext(request))
