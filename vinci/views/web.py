from django.conf import settings
from django.http.response import HttpResponse, HttpResponseNotFound
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from django.utils import timezone
from django.utils.timezone import utc, make_aware
import datetime

from vinci.models import Notebook, Entry, Revision, Group, TimelineDay
import vinci.search_indexer as si


@login_required
def notebook_home(request, notebook_slug):
    sortby = settings.VINCI_DEFAULT_SEARCH_ORDER
    sortby = request.GET.get('sort', sortby)
    page = int(request.GET.get('page', 1))

    notebook = get_object_or_404(Notebook, slug=notebook_slug)

    # Check default mode
    default_mode = 'log'
    if notebook.default_mode:
        default_mode = notebook.default_mode

    mode = request.GET.get('mode', default_mode)
    sticky = request.GET.get('sticky', '')

    # Save mode as default unless sticky is set
    if notebook.default_mode != mode and sticky != 'false':
        notebook.default_mode = mode
        notebook.save()

    entries = notebook.entries.active()

    if mode == 'note':
        # Sort notes by last modified
        entries = entries.order_by('-last_modified', '-date')
    else:
        entries = entries.order_by(sortby)

    try:
        entries = Paginator(entries,
                            settings.VINCI_RESULTS_PER_PAGE).page(page)
    except EmptyPage:
        entries = []

    # Title tag
    title_tag = '::{}'.format(notebook.slug)

    labels = []

    context = {
        'title': title_tag,
        'mode': mode,
        'modes': settings.VINCI_MODE_LIST,
        'notebook': notebook,
        'entries': entries,
        'labels': labels,
        'page_type': 'list',
        'API_KEY': settings.VINCI_API_KEY,
    }

    # Get the template
    template = settings.VINCI_TEMPLATES[mode]['list']

    return HttpResponse(template.render(RequestContext(request, context)),
                        content_type="text/html")


@login_required
def notebook_settings(request, notebook_slug):
    notebook = get_object_or_404(Notebook, slug=notebook_slug)

    # Title tag
    title_tag = 'Settings — ::{}'.format(notebook.slug)

    context = {
        'title': title_tag,
        'notebook': notebook,
        'modes': settings.VINCI_MODE_LIST,
        'statuses': [{'value': s[0], 'label': s[1]} for s in Notebook.STATUS],
        'groups': [{'value': g.name, 'label': g.name} for g in Group.objects.all()],
        'page_type': 'settings',
        'API_KEY': settings.VINCI_API_KEY,
    }

    return render_to_response('vinci/notebook_settings.html',
                              context,
                              RequestContext(request),
                              )


@login_required
def entry_detail(request, notebook_slug, entry_slug):
    try:
        entry = Entry.objects.from_slug(entry_slug, notebook_slug)
    except Entry.DoesNotExist:
        return HttpResponseNotFound('Entry does not exist.')

    # Check default mode
    default_mode = 'log'
    if entry.notebook.default_mode:
        default_mode = entry.notebook.default_mode

    mode = request.GET.get('mode', default_mode)
    sticky = request.GET.get('sticky', '')

    # Save mode as default unless sticky is set
    if entry.notebook.default_mode != mode and sticky != 'false':
        entry.notebook.default_mode = mode
        entry.notebook.save()

    # Title tag
    if entry.title:
        slug = entry.title
    else:
        slug = '{} ({})'.format(str(entry.date)[0:10], entry.id)

    title_tag = '{} — ::{}'.format(slug, entry.notebook.slug)

    context = {
        'title': title_tag,
        'mode': mode,
        'modes': settings.VINCI_MODE_LIST,
        'notebook': entry.notebook,
        'entry': entry,
        'page_type': 'detail',
        'API_KEY': settings.VINCI_API_KEY,
    }

    # Get the template
    template = settings.VINCI_TEMPLATES[mode]['detail']
    return HttpResponse(template.render(RequestContext(request, context)),
                        content_type="text/html")


@login_required
def revision_detail(request, notebook_slug, entry_slug, revision_id):
    mode = request.GET.get('mode', 'log')

    try:
        entry = Entry.objects.from_slug(entry_slug, notebook_slug)
    except Entry.DoesNotExist:
        return HttpResponseNotFound('Entry does not exist.')

    try:
        revision = Revision.objects.get(id=revision_id)
    except Revision.DoesNotExist:
        return HttpResponseNotFound('Revision does not exist.')

    # Check default mode
    default_mode = 'log'
    if entry.notebook.default_mode:
        default_mode = entry.notebook.default_mode

    mode = request.GET.get('mode', default_mode)
    sticky = request.GET.get('sticky', '')

    # Save mode as default unless sticky is set
    if entry.notebook.default_mode != mode and sticky != 'false':
        entry.notebook.default_mode = mode
        entry.notebook.save()

    # Title tag
    if entry.slug:
        slug = entry.slug
    else:
        slug = entry.id

    title_tag = '{}.{} — ::{}'.format(slug, revision.id, entry.notebook.slug)

    context = {
        'title': title_tag,
        'mode': mode,
        'modes': settings.VINCI_MODE_LIST,
        'notebook': entry.notebook,
        'entry': entry,
        'revision': revision,
        'page_type': 'detail',
        'API_KEY': settings.VINCI_API_KEY,
    }

    # Get the template
    template = settings.VINCI_TEMPLATES[mode]['detail']

    return HttpResponse(template.render(RequestContext(request, context)),
                        content_type="text/html")


@login_required
def notebooks_list(request):
    groups = Group.objects.all()
    active_notebooks = Notebook.objects.active()
    ungrouped_notebooks = active_notebooks.filter(group__isnull=True).order_by('name')

    if active_notebooks.count() == 0:
        blank_slate = True
    else:
        blank_slate = False

    # Get all the tags
    from taggit.models import Tag
    tags = Tag.objects.all().order_by('slug')

    context = {
        'title': 'All Notebooks',
        'groups': groups,
        'ungrouped_notebooks': ungrouped_notebooks,
        'tags': tags,
        'page_type': 'all',
        'blank_slate': blank_slate,
        'API_KEY': settings.VINCI_API_KEY,
    }

    return render_to_response('vinci/index.html',
                              context,
                              RequestContext(request),
                              )


@login_required
def diary_home(request):
    """ Shows calendar for diary mode. """

    date = request.GET.get('date', None)

    context = {
        'title': '/diary',
        'today': date,
        'page_type': 'diary',
        'API_KEY': settings.VINCI_API_KEY,
    }

    return render_to_response('vinci/diary.html',
                              context,
                              RequestContext(request),
                              )


@login_required
def diary_detail(request, day):
    """ Get every entry (log/journal) from the specified day, ordered by notebook. """

    # Note: day needs to be YYYY-MM-DD form

    # Convert date to a datetime object
    current_tz = timezone.get_current_timezone()
    the_date = datetime.datetime.strptime(day, "%Y-%m-%d")
    beginning = the_date.replace(hour=0, minute=0, second=0, tzinfo=current_tz)
    end = the_date.replace(hour=23, minute=59, second=59, tzinfo=current_tz)

    # Convert to UTC
    beginning_utc = beginning.astimezone(utc)
    end_utc = end.astimezone(utc)

    # Get all the entries on that day
    entries = Entry.objects.filter(status='active',
                                   date__gte=beginning_utc,
                                   date__lte=end_utc)

    # Sort by date, notebook
    entries = entries.order_by('date', 'notebook__name')

    # Get yesterday/tomorrow dates
    tomorrow = the_date + datetime.timedelta(days=1)
    tomorrow_slug = tomorrow.isoformat()[:10]
    yesterday = the_date - datetime.timedelta(days=1)
    yesterday_slug = yesterday.isoformat()[:10]

    context = {
        'title': '{} — /diary'.format(day),
        'entries': entries,
        'today': the_date,
        'tomorrow': {
            'slug': tomorrow_slug,
            'label': tomorrow,
        },
        'yesterday': {
            'slug': yesterday_slug,
            'label': yesterday,
        },
        'page_type': 'diary_detail',
        'API_KEY': settings.VINCI_API_KEY,
    }

    # Get the template
    template = settings.VINCI_TEMPLATES['log']['list']

    return HttpResponse(template.render(RequestContext(request, context)),
                        content_type="text/html")


@login_required
def search_notebook(request, notebook_slug):
    notebook = get_object_or_404(Notebook, slug=notebook_slug)
    return _search(request, request.GET.get('q'), notebook)


@login_required
def search_notebook_tags(request, notebook_slug, tag):
    notebook = get_object_or_404(Notebook, slug=notebook_slug)
    return _search(request, 'tag:{}'.format(tag), notebook)


@login_required
def search_all(request):
    return _search(request, request.GET.get('q'))


@login_required
def search_all_tags(request, tag):
    return _search(request, 'tag:{}'.format(tag))


def _search(request, query, notebook=None):
    sortby = request.GET.get('sort', settings.VINCI_DEFAULT_SEARCH_ORDER)
    page = int(request.GET.get('page', 1))
    tagview = False

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

        entries = si.search(**search_params)
        entries = Paginator(entries, settings.VINCI_RESULTS_PER_PAGE)
        total = entries.count
        entries = entries.page(page)

        # Tag view
        if 'tag:' in query:
            tagview = True

        # Convert tags in queries back to hashtag syntax
        query = query.replace('tag:', '#')

    mode = 'log'

    context = {
        'title': '{} — /search'.format(query),
        'query': query,
        'entries': entries,
        'total': total,
        'mode': mode,
        'modes': settings.VINCI_MODE_LIST,
        'tagview': tagview,
        'page_type': 'list',
        'search': True,
        'API_KEY': settings.VINCI_API_KEY,
    }

    if notebook:
        context['title'] = '{}{}{}'.format(context['title'], settings.VINCI_SITE_TITLE_SEP, notebook.name)
        context['notebook'] = notebook

    # Get the template
    template = settings.VINCI_TEMPLATES[mode]['search']

    return HttpResponse(template.render(RequestContext(request, context)),
                        content_type="text/html")


@login_required
def prefs_view(request):
    context = {
        'title': 'Preferences',
        'API_KEY': settings.VINCI_API_KEY,
    }

    return render_to_response('vinci/prefs.html',
                              context,
                              RequestContext(request),
                              )


@login_required
def overview(request):
    # See if we want to limit it to a specific notebook
    notebook = request.GET.get('notebook', '')

    if notebook != '':
        # Get notebook entries
        entries = Entry.objects.filter(notebook__slug=notebook)
    else:
        # Get all the entries
        entries = Entry.objects.all().order_by('date')

    years = {}

    import calendar

    for e in entries:
        d = e.date

        if d.year not in years:
            years[d.year] = {
                'label': d.year,
                'total': 1,
                'months': {},
            }
        else:
            years[d.year]['total'] += 1

        month = calendar.month_abbr[d.month]

        if d.month not in years[d.year]['months']:
            years[d.year]['months'][d.month] = {
                'label': month,
                'key': d.month,
                'total': 1,
                'days': {},
            }
        else:
            years[d.year]['months'][d.month]['total'] += 1
        
        if d.day not in years[d.year]['months'][d.month]['days']:
            years[d.year]['months'][d.month]['days'][d.day] = 1
        else:
            years[d.year]['months'][d.month]['days'][d.day] += 1

    # Sort years
    year_list = []

    for year_key in list(sorted(years)):
        month_list = []

        for month_key in list(sorted(years[year_key]['months'])):
            day_list = []

            for day_key in list(sorted(years[year_key]['months'][month_key]['days'])):
                day_list.append({
                    'label': day_key,
                    'slug': '{}-{:0>2}-{:0>2}'.format(year_key, years[year_key]['months'][month_key]['key'], day_key),
                    'total': years[year_key]['months'][month_key]['days'][day_key],
                })

            month_list.append({
                'label': years[year_key]['months'][month_key]['label'],
                'total': years[year_key]['months'][month_key]['total'],
                'key': years[year_key]['months'][month_key]['key'],
                'days': day_list,
            })

        year_list.append({
            'label': years[year_key]['label'],
            'total': years[year_key]['total'],
            'months': month_list,
        })

    context = {
        'title': 'Overview',
        'page_type': 'overview',
        'years': year_list,
        'notebook_filter': notebook,
        'API_KEY': settings.VINCI_API_KEY,
    }

    return render_to_response('vinci/overview.html',
                              context,
                              RequestContext(request),
                              )


@login_required
def timeline(request):
    entries = TimelineDay.objects.all()

    context = {
        'title': 'Timeline',
        'entries': entries,
        'page_type': 'timeline',
        'API_KEY': settings.VINCI_API_KEY,
    }

    return render_to_response('vinci/timeline.html',
                              context,
                              RequestContext(request),
                              )
