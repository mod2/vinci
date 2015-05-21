from django.conf import settings
from django.http.response import HttpResponseNotFound
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from vinci.models import Notebook, Entry, Revision, Group
import vinci.search_indexer as si


@login_required
def notebook_home(request, notebook_slug):
    notebook = get_object_or_404(Notebook, slug=notebook_slug)

    # Redirect to the default section for this notebook
    return redirect('notebook_section', notebook_slug=notebook_slug, section=notebook.default_section)


@login_required
def notebook_settings(request, notebook_slug):
    notebook = get_object_or_404(Notebook, slug=notebook_slug)

    context = {
        'title': notebook.name,
        'notebook': notebook,
        'scope': 'notebook',
        'statuses': [{'value': s[0], 'label': s[1]} for s in Notebook.STATUS],
        'groups': [{'value': g.name, 'label': g.name} for g in Group.objects.all()],
        'page_type': 'settings',
    }

    return render_to_response('vinci/notebook_settings.html',
                              context,
                              RequestContext(request),
                              )


@login_required
def notebook_section(request, notebook_slug, section):
    sortby = request.GET.get('sort', settings.VINCI_DEFAULT_SEARCH_ORDER)
    page = int(request.GET.get('page', 1))

    notebook = get_object_or_404(Notebook, slug=notebook_slug)

    entries = notebook.entries.filter(entry_type=section).order_by(sortby)
    entries = Paginator(entries, settings.VINCI_RESULTS_PER_PAGE).page(page)

    notebooks = Notebook.objects.filter(status='active').order_by('name')

    context = {
        'title': notebook.name,
        'notebook': notebook,
        'notebooks': notebooks,
        'section': section,
        'scope': 'section',
        'entries': entries,
        'page_type': 'list',
    }

    return render_to_response('vinci/list.html',
                              context,
                              RequestContext(request),
                              )


@login_required
def entry_detail(request, notebook_slug, section, entry_slug):
    try:
        entry = Entry.objects.from_slug(entry_slug, notebook_slug)
    except Entry.DoesNotExist:
        return HttpResponseNotFound('Entry does not exist.')

    context = {
        'title': entry.notebook.name,
        'notebook': entry.notebook,
        'entry': entry,
        'section': section,
        'scope': 'section',
        'page_type': 'detail',
    }

    return render_to_response('vinci/entry.html',
                              context,
                              RequestContext(request),
                              )


@login_required
def revision_detail(request, notebook_slug, section, entry_slug, revision_id):
    try:
        entry = Entry.objects.from_slug(entry_slug, notebook_slug)
    except Entry.DoesNotExist:
        return HttpResponseNotFound('Entry does not exist.')

    try:
        revision = Revision.objects.get(id=revision_id)
    except Revision.DoesNotExist:
        return HttpResponseNotFound('Revision does not exist.')

    context = {
        'title': entry.notebook.name,
        'notebook': entry.notebook,
        'entry': entry,
        'revision': revision,
        'section': section,
        'scope': 'section',
        'page_type': 'detail',
    }

    return render_to_response('vinci/entry.html',
                              context,
                              RequestContext(request),
                              )


@login_required
def notebooks_list(request):
    groups = Group.objects.all()
    ungrouped_notebooks = Notebook.objects.active().filter(group__isnull=True).order_by('name')

    context = {
        'title': 'All Notebooks',
        'groups': groups,
        'ungrouped_notebooks': ungrouped_notebooks,
        'scope': 'all',
        'page_type': 'all',
    }

    return render_to_response('vinci/index.html',
                              context,
                              RequestContext(request),
                              )


@login_required
def search_notebook(request, notebook_slug):
    notebook = get_object_or_404(Notebook, slug=notebook_slug)
    return _search(request, request.GET.get('q'), notebook)


@login_required
def search_notebook_tags(request, notebook_slug, tag):
    notebook = get_object_or_404(Notebook, slug=notebook_slug)
    return _search(request, 'tag:{}'.format(tag), notebook)


@login_required
def search_notebook_section(request, notebook_slug, section):
    notebook = get_object_or_404(Notebook, slug=notebook_slug)
    return _search(request, request.GET.get('q'), notebook, section)


@login_required
def search_all(request):
    return _search(request, request.GET.get('q'))


@login_required
def search_all_tags(request, tag):
    return _search(request, 'tag:{}'.format(tag))


def _search(request, query, notebook=None, section=None):
    sortby = request.GET.get('sort', settings.VINCI_DEFAULT_SEARCH_ORDER)
    page = int(request.GET.get('page', 1))

    if query is None:
        entries = Paginator([], settings.VINCI_RESULTS_PER_PAGE).page(1)
    else:
        search_params = {
            'query_string': query,
            'page': page,
            'sort_order': sortby,
        }

        if section:
            search_params['entry_type'] = section

        if notebook:
            search_params['notebook'] = notebook

        #entries, __, __ = si.search(**search_params)
        entries= si.search(**search_params)
        entries = Paginator(entries, settings.VINCI_RESULTS_PER_PAGE)
        total = entries.count
        entries = entries.page(page)

        notebooks = Notebook.objects.filter(status='active').order_by('name')

        # Convert tags in queries back to hashtag syntax
        query = query.replace('tag:', '#')

    scope = 'all'
    if notebook is not None:
        scope = 'notebook'
    if section is not None:
        scope = 'section'

    context = {
        'title': '{}{}Search'.format(query, settings.VINCI_SITE_TITLE_SEP),
        'query': query,
        'entries': entries,
        'total': total,
        'section': section,
        'scope': scope,
        'notebooks': notebooks,
        'page_type': 'list',
        'search': True,
    }

    if notebook:
        context['title'] = '{}{}{}'.format(context['title'], settings.VINCI_SITE_TITLE_SEP, notebook.name)
        context['notebook'] = notebook

    return render_to_response('vinci/list.html',
                              context,
                              RequestContext(request),
                              )
