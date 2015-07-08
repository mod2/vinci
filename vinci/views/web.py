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

from vinci.models import Notebook, Entry, Revision, Group, Label, List, Card
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
    sortby = settings.VINCI_DEFAULT_SEARCH_ORDER
    sortby = sortby if section != 'note' else '-last_modified'
    sortby = request.GET.get('sort', sortby)
    page = int(request.GET.get('page', 1))

    notebooks = Notebook.objects.filter(status='active').order_by('name')
    notebook = get_object_or_404(Notebook, slug=notebook_slug)

    if section == 'todo':
        template = 'todos'
        labels = Label.objects.all()
        entries = []
    else:
        entries = (notebook.entries
                .active()
                .filter(entry_type=section)
                .order_by(sortby)
                )
        entries = Paginator(entries, settings.VINCI_RESULTS_PER_PAGE).page(page)

        template = 'entries'
        labels = []

    context = {
        'title': notebook.name,
        'notebook': notebook,
        'notebooks': notebooks,
        'section': section,
        'scope': 'section',
        'entries': entries,
        'labels': labels,
        'page_type': 'list',
    }

    if section == 'todo':
        context['lists'] = notebook.get_active_lists()
        context['num_lists'] = len(context['lists']) + 1

    return render_to_response('vinci/{}.html'.format(template),
                              context,
                              RequestContext(request),
                              )


@login_required
def card_detail(request, notebook_slug, card_id):
    try:
        card = Card.objects.get(id=card_id, list__notebook__slug=notebook_slug)
    except Card.DoesNotExist:
        return HttpResponseNotFound('Card does not exist.')

    template = 'card'
    labels = Label.objects.all()
    notebooks = Notebook.objects.filter(status='active').order_by('name')
    section = 'todo'

    context = {
        'title': card.title,
        'notebook': card.list.notebook,
        'notebooks': notebooks,
        'card': card,
        'labels': labels,
        'section': section,
        'scope': 'section',
        'page_type': 'detail',
    }

    if section == 'todo':
        context['lists'] = card.list.notebook.get_active_lists()
        context['num_lists'] = len(context['lists']) + 1
        context['num_lists_sub_one'] = context['num_lists'] - 1

    return render_to_response('vinci/card.html',
                              context,
                              RequestContext(request),
                              )


@login_required
def entry_detail(request, notebook_slug, section, entry_slug):
    try:
        entry = Entry.objects.from_slug(entry_slug, notebook_slug)
    except Entry.DoesNotExist:
        return HttpResponseNotFound('Entry does not exist.')

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
def today(request):
    # Get all Today lists
    today_lists = List.objects.filter(title='Today', status='active').order_by('notebook__name')

    section = 'today'

    context = {
        'title': 'Today',
        'today_lists': today_lists,
        'section': section,
        'scope': 'all',
        'page_type': 'today',
    }

    return render_to_response('vinci/today.html',
                              context,
                              RequestContext(request),
                              )


@login_required
def diary(request, day):
    """ Get every entry (log/journal) from the specified day, ordered by notebook. """

    # Note: day needs to be YYYY-MM-DD form

    # Get list of all active notebooks (for add tray)
    notebooks = Notebook.objects.filter(status='active').order_by('name')

    # Convert date to a datetime object
    current_tz = timezone.get_current_timezone()
    the_date = datetime.strptime(day, "%Y-%m-%d")
    beginning = the_date.replace(hour=0, minute=0, second=0, tzinfo=current_tz)
    end = the_date.replace(hour=23, minute=59, second=59, tzinfo=current_tz)

    print(beginning, end)

    # Convert to UTC
    #local_beginning = current_tz.localize(beginning, is_dst=None)
    #local_end = current_tz.localize(end, is_dst=None)
    #beginning_utc = local_beginning.astimezone(utc)
    #end_utc = local_end.astimezone(utc)

    # Get all the entries on that day
    entries = Entry.objects.filter(status='active',
                                   date__gte=beginning,
                                   date__lte=end)
    print(entries)

    # Limit it to just logs and journals
    entries = entries.filter(Q(entry_type='log')
                            | Q(entry_type='journal'))

    # Sort by notebook and date and date and date and date
    entries = entries.order_by('notebook__name', 'date')

    # Now group them into notebooks
    diary_notebooks = []
    for entry in entries:
        try:
            nb_slug = diary_notebooks[-1]['slug']

            if entry.notebook.slug == nb_slug:
                # Same notebook as the last entry
                diary_notebooks[-1]['entries'].append(entry)
            else:
                # New notebook
                diary_notebooks.append({
                    'name': entry.notebook.name,
                    'slug': entry.notebook.slug,
                    'entries': [entry],
                })
        except IndexError as e:
            # No notebooks in the list yet
            diary_notebooks.append({
                'name': entry.notebook.name,
                'slug': entry.notebook.slug,
                'entries': [],
            })

    context = {
        'title': 'Diary ({})'.format(day),
        'notebooks': notebooks,
        'diary_notebooks': diary_notebooks,
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
