from django.conf import settings
from django.http.response import HttpResponseNotFound
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from django.utils import timezone
from django.utils.timezone import utc, make_aware
from datetime import datetime

from vinci.models import Notebook, Section, Entry, Revision, Group
import vinci.search_indexer as si

from vinci.utils import get_sections_for_notebook


@login_required
def notebook_home(request, notebook_slug):
    notebook = get_object_or_404(Notebook, slug=notebook_slug)

    if notebook.default_section:
        section = notebook.default_section
    else:
        section = None

    # Redirect to the default section for this notebook
    return redirect('notebook_section', notebook_slug=notebook_slug, section=section)


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
def notebook_section(request, notebook_slug, section_slug):
    sortby = settings.VINCI_DEFAULT_SEARCH_ORDER
    sortby = request.GET.get('sort', sortby)
    page = int(request.GET.get('page', 1))

    notebook = get_object_or_404(Notebook, slug=notebook_slug)

    if section_slug:
        section = get_object_or_404(Section, slug=section_slug, notebook=notebook)
    else:
        section = None

    entries = notebook.entries.active()
    if section:
        entries = entries.filter(section=section)
    entries = entries.order_by(sortby)
    entries = Paginator(entries, settings.VINCI_RESULTS_PER_PAGE).page(page)

    # Get sections (for sidebar list)
    sections = get_sections_for_notebook(notebook)

    template = 'entries'
    labels = []

    context = {
        'title': notebook.name,
        'notebook': notebook,
        'section': section,
        'sections': sections,
        'scope': 'section',
        'entries': entries,
        'labels': labels,
        'page_type': 'list',
    }

    return render_to_response('vinci/{}.html'.format(template),
                              context,
                              RequestContext(request),
                              )


@login_required
def entry_detail(request, notebook_slug, section_slug, entry_slug):
    try:
        entry = Entry.objects.from_slug(entry_slug, section_slug, notebook_slug)
    except Entry.DoesNotExist:
        return HttpResponseNotFound('Entry does not exist.')

    try:
        section = Section.objects.get(slug=section_slug, notebook__slug=notebook_slug)
    except Section.DoesNotExist:
        return HttpResponseNotFound('Section does not exist.')

    notebooks = Notebook.objects.filter(status='active').order_by('name')

    context = {
        'title': entry.notebook.name,
        'notebook': entry.notebook,
        'notebooks': notebooks,
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
def revision_detail(request, notebook_slug, section_slug, entry_slug, revision_id):
    try:
        if section_slug:
            entry = Entry.objects.from_slug(entry_slug, section_slug, notebook_slug)
        else:
            entry = Entry.objects.from_slug(entry_slug, None, notebook_slug)
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

    if len(Notebook.objects.active()) == 0:
        blank_slate = True
    else:
        blank_slate = False

    context = {
        'title': 'All Notebooks',
        'groups': groups,
        'ungrouped_notebooks': ungrouped_notebooks,
        'scope': 'all',
        'page_type': 'all',
        'blank_slate': blank_slate,
    }

    return render_to_response('vinci/index.html',
                              context,
                              RequestContext(request),
                              )


@login_required
def diary(request, day):
    """ Get every entry (log/journal) from the specified day, ordered by notebook. """

    # Note: day needs to be YYYY-MM-DD form

    # Get list of all active notebooks (for add tray)
    notebooks = Notebook.objects.exclude(status='deleted').order_by('name')

    # Convert date to a datetime object
    current_tz = timezone.get_current_timezone()
    the_date = datetime.strptime(day, "%Y-%m-%d")
    beginning = the_date.replace(hour=0, minute=0, second=0, tzinfo=current_tz)
    end = the_date.replace(hour=23, minute=59, second=59, tzinfo=current_tz)

    # Convert to UTC
    beginning_utc = beginning.astimezone(utc)
    end_utc = end.astimezone(utc)

    # Get all the entries on that day
    entries = Entry.objects.filter(status='active',
                                   date__gte=beginning_utc,
                                   date__lte=end_utc)

    # Limit it to just logs and journals
    entries = entries.filter(Q(entry_type='log') | Q(entry_type='journal'))

    # Sort by notebook and date
    entries = entries.order_by('date', 'notebook__name')

    context = {
        'title': 'Diary ({})'.format(day),
        'notebooks': notebooks,
        'entries': entries,
        'section': 'log',
        'scope': 'all',
        'page_type': 'diary',
    }

    return render_to_response('vinci/diary.html',
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
def search_notebook_section(request, notebook_slug, section_slug):
    notebook = get_object_or_404(Notebook, slug=notebook_slug)
    section = get_object_or_404(Section, slug=section_slug, notebook=notebook)
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
            search_params['section'] = section

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
        'title': 'Search',
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

    return render_to_response('vinci/entries.html',
                              context,
                              RequestContext(request),
                              )


@login_required
def prefs_view(request):
    labels = Label.objects.all()

    context = {
        'labels': labels,
        'title': 'Preferences',
    }
    return render_to_response('vinci/prefs.html',
                              context,
                              RequestContext(request),
                              )
