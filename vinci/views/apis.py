import datetime
import json

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import authentication
from rest_framework import exceptions
from rest_framework import viewsets
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response as APIResponse
from rest_framework.views import APIView
from taggit.models import Tag

from vinci import models, serializers, search_indexer as si
from vinci.utils import get_or_create_notebook, get_or_create_section, parse_payload

def _reorder_items(model_qs, orders, owner_id=None):
    """
    Given a queryset and an orders dict, sets the order of the items.
    Possibly also moves the items to a new owner if owner_id is provided.

    Arguments:
        model_qs - A QuerySet that can be used to get all of the items that
                   should be updated.
        orders - A dict where the keys are the ids of the items to be changed
                 and the values are the order numbers to be saved. {"1": 3,...}
        owner_id - OPTIONAL id for an owner to move all of the items to.
    """
    objects = model_qs.filter(pk__in=[int(pk) for pk in orders.keys()])
    rtn_orders = {}
    for obj in objects:
        obj.order = orders[str(obj.pk)]
        if owner_id:
            obj.list_id = owner_id
        obj.save()
        rtn_orders[obj.pk] = obj.order
    return rtn_orders


def _validate_custom_methods(request, op_type):
    operation = request.data.get('operation', 'default')
    payload = None
    payload_type = ''
    if operation == 'default':
        return False, None

    if operation == '{}-ordering'.format(op_type):
        payload = request.data.get('{}_orders'.format(op_type))
        payload_type = 'ordering'
    if operation == '{}-copy'.format(op_type):
        payload = ''
        payload_type = 'copy'

    return (payload_type, payload)


class ReOrderMixin():
    def patch(self, request):
        """
        Reorder items specified by the request.
        """
        op_type = self.serializer_class.Meta.model.__name__.lower()
        queryset = self.queryset

        type_, orders = _validate_custom_methods(request, op_type)
        if type_ is 'ordering' and orders is None:
            msg = {'error': '{}_orders is required'.format(op_type)}
            return APIResponse(msg, status=400)
        elif type_ is 'ordering' and orders:
            rtn_orders = _reorder_items(queryset, orders)
            return APIResponse(rtn_orders)
        else:
            return super().patch(request)


class ReOrderChildrenMixin():
    partial_update_model = None
    partial_update_queryset = None

    def partial_update(self, request, pk=None):
        if not self.partial_update_model:
            raise Exception("ReOrderChildrenMixin not configured properly.")
        op_type = self.partial_update_model.__name__.lower()
        queryset = self.partial_update_model.objects.all()
        if self.partial_update_queryset:
            queryset = self.partial_update_queryset
        owner_id = pk

        type_, orders = _validate_custom_methods(request, op_type)

        if type_ is 'ordering' and orders is None:
            msg = {'error': '{}_orders is required'.format(op_type)}
            return APIResponse(msg, status=400)
        elif type_ is 'ordering' and orders:
            rtn_orders = _reorder_items(queryset, orders, owner_id=owner_id)
            return APIResponse(rtn_orders)
        else:
            # No operation provided, perform normal patch (partial_update).
            return super().partial_update(request, pk)


class APIKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        username = settings.VINCI_DEFAULT_API_KEY_USERNAME
        api_key = request.META.get('HTTP_X_API_KEY')

        if not username or not api_key or api_key != settings.VINCI_API_KEY:
            return None

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')
        return (user, None)


class APIResponseNotFound(APIResponse):
    def __init__(self, message='Not Found', **kwargs):
        detail = {'detail': message}
        super().__init__(data=detail, status=404, **kwargs)


class NotebookLimitMixin(object):
    def get_queryset(self):
        qs = models.Entry.objects.all()
        notebook_slug = self.kwargs.get('notebook_slug', '')
        if notebook_slug:
            qs = qs.filter(notebook__slug=notebook_slug)
        return qs


class EntryListAPIView(NotebookLimitMixin, ListCreateAPIView):
    """
    List of entries and notebook operations. Different methods determine what is
    done.

    - **GET** List the entries for the current notebook.
    - **POST** Create a new entry attached to the current notebook.
    - **PUT** Edit the current notebook's name, status, group, or sections.
    - **DELETE** Delete the current notebook (sets the status to deleted).
    """
    serializer_class = serializers.EntrySerializer

    def post(self, request, notebook_slug):
        """Create a new Entry."""

        content = request.data.get('content')
        section_slug = request.data.get('section')

        payload = parse_payload(content) 

        # Get or create notebook/section
        if 'notebook' in payload:
            notebook_slug = payload['notebook']
            payload['notebook'] = get_or_create_notebook(notebook_slug)
        else:
            # Default to the notebook we're in
            notebook = get_or_create_notebook(notebook_slug)

        if 'section' in payload:
            section_slug = payload['section']
            payload['section'] = get_or_create_section(section_slug, notebook_slug)
        else:
            if section_slug:
                # Section passed in
                payload['section'] = get_or_create_section(section_slug, notebook_slug)
            elif notebook.default_section is None:
                # Try the notebook's default section
                payload['section'] = notebook.default_section

        if len(payload['content'].strip()) > 0:
            entry = models.Entry.objects.create(**payload)

            si.add_index(entry)
            e = serializers.EntrySerializer(entry)

            return APIResponse(e.data)
        return APIResponse({'detail': 'No content to save.'}, status=400)

    def put(self, request, notebook_slug):  # noqa too complex
        """Update an existing Notebook."""

        notebook = get_object_or_404(models.Notebook, slug=notebook_slug)

        name = request.data.get('name')
        status = request.data.get('status')
        group = request.data.get('group')
        default_section = request.data.get('default_section')

        if name is not None:
            notebook.name = name

        if status is not None and status in models.Notebook.STATUS:
            notebook.status = status

        if group is not None:
            new_group = models.Group.objects.get(name=group)
            if new_group:
                notebook.group = new_group

        if default_section is not None:
            try:
                if default_section == 'home':
                    notebook.default_section = None
                else:
                    section = models.Section.objects.get(slug=default_section, notebook=notebook)
                    notebook.default_section = section
            except models.Section.DoesNotExist:
                return APIResponseNotFound('Section does not exist.')

        notebook.save()

        nb = serializers.NotebookSerializer(notebook,
                                            context={'request': request})

        return APIResponse(nb.data)

    def delete(self, request, notebook_slug):
        """Delete a Notebook. Sets the status to 'deleted'."""
        notebook = get_object_or_404(models.Notebook, slug=notebook_slug)
        notebook.status = notebook.STATUS.deleted
        nb = serializers.NotebookSerializer(notebook,
                                            context={'request': request})
        notebook.delete()
        return APIResponse(nb.data)


class EntryDetailAPIView(NotebookLimitMixin, APIView):
    """
    A single entry detail
    """
    serializer_class = serializers.EntrySerializer

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        qs = super().get_queryset()

        if slug is None and len(self.args) > 1:
            slug = self.args[1]
        elif slug is None:
            slug = ''
        slug = slug.strip()
        if slug:
            try:
                qs = qs.from_slug(slug)
            except models.Entry.DoesNotExist:
                qs = None

        return qs

    get_entry_for_request = get_queryset

    def get(self, request, *args, **kwargs):
        entry = self.get_entry_for_request()
        if entry:
            return APIResponse(self.serializer_class(entry).data)
        else:
            return APIResponseNotFound('No entry found.')

    def put(self, request, *args, **kwargs):
        """Update an existing Entry."""
        entry = self.get_entry_for_request()
        content = request.data.get('content')
        date = request.data.get('date', '')

        tag_list = request.data.get('tags', '')
        if tag_list:
            tags = [t.strip() for t in tag_list.split(',')]
        else:
            tags = None

        if entry:
            entry.content = content
            entry.title = request.data.get('title', '')

            if date:
                entry.date = datetime.datetime.strptime(date,
                                                        models.DATETIME_FORMAT)

            entry.save()

            if tags:
                entry.tags.set(*tags)
            else:
                entry.tags.clear()

            si.update_index(entry)
            e = self.serializer_class(entry).data

            return APIResponse(e)
        else:
            return APIResponseNotFound('No entry found.')

    def delete(self, request, *args, **kwargs):
        entry = self.get_entry_for_request()
        if entry:
            e = self.serializer_class(entry).data
            entry.delete()
            si.delete_from_index(entry)
            return APIResponse(e)
        else:
            return APIResponseNotFound('No entry found.')


class NotebookListAPIView(ListCreateAPIView):
    """
    List of all the notebooks.

    ## Optional Parameters

    * `status` - active (default), archived, deleted

    ## Examples

    * `GET /api/?status=archived` Return list of all the archived notebooks.
    """
    serializer_class = serializers.NotebookSerializer

    def get_queryset(self):
        qs = models.Notebook.objects
        status = self.request.GET.get('status', models.Notebook.STATUS.active)
        if status == models.Notebook.STATUS.archived:
            qs = qs.archived()
        elif status == models.Notebook.STATUS.deleted:
            qs = qs.deleted()
        else:  # show active
            qs = qs.active()
        return qs

    def post(self, request):
        """ POST payload. """
        response = add_payload(request)

        if 'error' in response:
            return APIResponse({'detail': response['error']}, status=response['status'])
        else:
            return APIResponse(response)


class NotebookDetailAPIView(APIView):
    """
    A single notebook detail
    """
    serializer_class = serializers.NotebookSerializer

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        qs = super().get_queryset()

        if slug is None and len(self.args) > 1:
            slug = self.args[1]
        elif slug is None:
            slug = ''
        slug = slug.strip()
        if slug:
            try:
                qs = qs.from_slug(slug)
            except models.Notebook.DoesNotExist:
                qs = None

        return qs

    get_notebook_for_request = get_queryset

    def get(self, request, *args, **kwargs):
        notebook = self.get_notebook_for_request()
        if notebook:
            return APIResponse(self.serializer_class(notebook).data)
        else:
            return APIResponseNotFound('No notebook found.')

    def put(self, request, *args, **kwargs):
        """Update an existing Notebook."""
        notebook = self.get_notebook_for_request()
        name = request.data.get('name', '')
        status = request.data.get('status', '')
        group = request.data.get('group', '')
        default_section = request.data.get('default_section', '')

        if notebook:
            if name != '':
                notebook.name = name

            if status != '':
                notebook.status = status

            if group != '':
                new_group = models.Group.objects.get(name=group)
                if new_group:
                    notebook.group = new_group

            if default_section != '':
                try:
                    if default_section == 'home':
                        notebook.default_section = None
                    else:
                        section = models.Section.objects.get(slug=default_section, notebook=notebook)
                        notebook.default_section = section
                except models.Section.DoesNotExist:
                    return APIResponseNotFound('Section does not exist.')

            notebook.save()

            si.update_index(notebook)

            n = self.serializer_class(notebook).data
            return APIResponse(n)
        else:
            return APIResponseNotFound('No notebook found.')

    def delete(self, request, *args, **kwargs):
        notebook = self.get_notebook_for_request()
        if notebook:
            n = self.serializer_class(notebook).data
            notebook.delete()
            return APIResponse(n)
        else:
            return APIResponseNotFound('No notebook found.')


class QuickJumpAPIView(APIView):
    """
    An endpoint that returns matching Notebooks and Pages.

    __Note__: **Set the HTTP_X_API_KEY to the value same as the VINCI_API_KEY
    setting.**

    ## Parameters:

    * `q` - The query to search for. *REQUIRED*

    ## Examples

    * GET `/api/quick-jump/?q={query}` Returns lists of all the pages and
    notebooks and sections that match the given query.

    """
    authentication_classes = (APIKeyAuthentication,)

    def get(self, request, *args, **kwargs):
        status = 'error'
        msg_label = 'message'
        msg = 'Bad Request'
        status_code = 400

        query = request.GET.get('q', '').strip().lower()
        if query:
            # See if there's a notebook specifier ("home.projects", for example)
            query, _, notebook_specifier = query.partition('.')

            # Get notebooks
            notebooks = (models.Notebook.objects
                         .filter(name__icontains=query)
                         )[:5]

            # Get sections
            sections = (models.Section.objects
                         .filter(name__icontains=query)
                         )[:5]

            # Get tags
            tags = Tag.objects.filter(name__icontains=query)[:5]

            # Get entries
            entries = models.Entry.objects.filter(title__icontains=query)

            if notebook_specifier:
                # Filter further by a specific notebook (allows user to resolve
                # pages with same name in different notebooks)
                notebook_slug_contains = {
                    'notebook__slug__icontains': notebook_specifier,
                }
                entries = entries.filter(**notebook_slug_contains)

                # Zero out notebooks/tags because we only want pages
                notebooks = []
                tags = []

            # Limit to top five entries
            entries = entries[:5]

            status = 'success'
            status_code = 200
            msg_label = 'results'

            notebook_list = []
            section_list = []
            page_list = []
            tag_list = []

            for notebook in notebooks:
                nb = {'name': notebook.name,
                      'slug': notebook.slug,
                      'url': notebook.get_absolute_url(),
                      }
                notebook_list.append(nb)

            for section in sections:
                s = {'name': str(section),
                     'slug': section.slug,
                     'url': section.get_absolute_url(),
                     }
                section_list.append(s)

            for entry in entries:
                page = {'name': entry.title,
                        'slug': entry.slug,
                        'notebook': entry.notebook.name,
                        'section': entry.section.name if entry.section else '',
                        'url': entry.get_absolute_url(),
                        }
                page_list.append(page)

            for tag in tags:
                tag_item = {'name': tag.name,
                            'slug': tag.slug,
                            'url': reverse('search_all_tags',
                                           kwargs={'tag': tag.slug}),
                            }
                tag_list.append(tag_item)

            msg = {
                'notebooks': notebook_list,
                'sections': section_list,
                'pages': page_list,
                'tags': tag_list,
            }
        else:
            msg = 'A query is required. Pass the q query param.'

        return APIResponse({'status': status, msg_label: msg},
                           status=status_code)


# Non-REST API views
def append_today(request, notebook_slug):
    """ Appends to today's entry, creating it if it's not there. """

    callback = request.GET.get('callback', '')
    section = request.GET.get('section', '')
    key = request.GET.get('key', '')

    if key != settings.VINCI_NON_REST_KEY:
        return JsonResponse({})

    if request.method == 'GET':
        content = request.GET.get('content')
    elif request.method == 'POST':
        content = request.POST.get('content')

    # Append/create the entry
    try:
        now = datetime.datetime.now()
        today = datetime.datetime(now.year, now.month, now.day)
        tomorrow = today + datetime.timedelta(days=1)

        # Notebook
        notebook = models.Notebook.objects.get(slug=notebook_slug)

        # Section
        if section != '':
            section = models.Section.objects.get(slug=section, notebook=notebook)
        else:
            section = notebook.default_section

        # Get first entry for today
        results = (models.Entry.objects
                   .filter(notebook=notebook,
                           section=section,
                           date__range=[today, tomorrow],
                           )
                   .order_by('date')
                   )[:1]

        if len(results) > 0:
            entry = results[0]

            # Get the text
            cur_rev = entry.current_revision

            # Add new revision with appended content
            new_revision = models.Revision()

            new_revision.entry = entry
            new_revision.content = cur_rev.content + content
            new_revision.parent = cur_rev
            new_revision.save()

            # Save the entry
            entry.save()
        else:
            # We don't have an entry today, so create it (strip it first
            # so there's no initial newline)

            kwargs = {'content': content.strip(),
                      'section': section,
                      'notebook': notebook,
                      }
            entry = models.Entry.objects.create(**kwargs)

        response = {
            'status': 'success',
            'id': entry.id,
        }

    except Exception as e:
        response = {
            'status': 'error',
            'message': '{}'.format(e),
        }

    if callback:
        # Redirect to callback
        response = HttpResponse("", status=302)
        response['Location'] = callback
        return response
    else:
        # Return JSON response
        return JsonResponse(response)


def add_entry(request, notebook_slug):
    """ Adds an entry to a notebook. """

    callback = request.GET.get('callback', '')
    key = request.GET.get('key', '')
    section = request.GET.get('section', '')

    if key != settings.VINCI_NON_REST_KEY:
        return JsonResponse({})

    if request.method == 'GET':
        content = request.GET.get('content')
    elif request.method == 'POST':
        content = request.POST.get('content')

    # Create the entry
    try:
        # Notebook
        notebook = models.Notebook.objects.get(slug=notebook_slug)

        if section == '':
            section = notebook.default_section

        kwargs = {'content': content.strip(),
                  'section': section,
                  'notebook': notebook,
                  }
        entry = models.Entry.objects.create(**kwargs)

        # Save the entry
        entry.save()

        response = {
            'status': 'success',
            'id': entry.id,
        }

    except Exception as e:
        response = {
            'status': 'error',
            'message': '{}'.format(e),
        }

    if callback:
        # Redirect to callback
        response = HttpResponse("", status=302)
        response['Location'] = callback
        return response
    else:
        # Return JSON response
        return JsonResponse(response)


def add_revision(request, notebook_slug, slug):  # noqa too complex
    """ Adds a new revision to an entry. """

    try:
        data = json.loads(request.body.decode(encoding='UTF-8'))

        content = data.get('content', '')
        title = data.get('title', '')
        tags = data.get('tags', '')
        date = data.get('date', '')
        new_notebook = data.get('notebook', '')

        # Notebook
        notebook = models.Notebook.objects.get(slug=notebook_slug)
        entry = models.Entry.objects.get(id=slug, notebook=notebook)

        # Create the revision
        if content:
            revision = models.Revision()
            revision.content = content.strip()
            revision.entry = entry
            revision.save()

        if title:
            entry.title = title

        if date:
            entry.date = datetime.datetime.strptime(date,
                                                    models.DATETIME_FORMAT)

        if tags:
            entry.tags.clear()
            if tags != '[CLEAR]':
                tags = [t.strip() for t in tags.split(',')]
                entry.tags.add(*tags)
                entry.save()

        if new_notebook:
            nb = models.Notebook.objects.get(slug=new_notebook)
            entry.notebook = nb

        entry.save()
        si.update_index(entry)

        response = {
            'status': 'success',
        }

        if content:
            response['revision_id'] = revision.id
            response['html'] = revision.html()

        if date:
            response['date'] = date

    except Exception as e:
        response = {
            'status': 'error',
            'message': '{}'.format(e),
        }

    # Return JSON response
    return JsonResponse(response)


def update_revision(request, notebook_slug, slug, revision_id):
    """ Update revision for an entry. """

    try:
        data = json.loads(request.body.decode(encoding='UTF-8'))

        content = data.get('content', '')
        title = data.get('title', '')
        tags = data.get('tags', '')
        date = data.get('date', '')
        new_notebook = data.get('notebook', '')

        notebook = models.Notebook.objects.get(slug=notebook_slug)
        entry = models.Entry.objects.get(id=slug, notebook=notebook)

        # Update it
        if content:
            revision = models.Revision.objects.get(id=revision_id)
            revision.content = content.strip()
            revision.save()

        if title:
            entry.title = title

        if date:
            entry.date = datetime.datetime.strptime(date,
                                                    models.DATETIME_FORMAT)

        if tags:
            entry.tags.clear()
            tags = [t.strip() for t in tags.split(',')]
            entry.tags.add(*tags)
            entry.save()  # TODO: Is this needed?

        if new_notebook:
            nb = models.Notebook.objects.get(slug=new_notebook)
            entry.notebook = nb

        entry.save()
        si.update_index(entry)

        response = {
            'status': 'success',
        }

        if content:
            response['revision_id'] = revision.id
            response['html'] = revision.html()

        if date:
            response['date'] = date

    except Exception as e:
        response = {
            'status': 'error',
            'message': '{}'.format(e),
        }

    # Return JSON response
    return JsonResponse(response)


def add_payload(request):
    """Add a payload from the content query parameter."""

    if hasattr(request, 'data'):
        content = request.data.get('content', '')
        notebook_slug = request.data.get('notebook', None)
        section_slug = request.data.get('section', None)
    else:
        content = request.GET.get('content', '')
        notebook_slug = request.GET.get('notebook', None)
        section_slug = request.GET.get('section', None)

    if content == '':
        return {
            'error': 'No content to save',
            'status': 400,
        }

    payload = parse_payload(content) 

    # Get or create notebook/section
    if 'notebook' in payload:
        notebook_slug = payload['notebook']
        payload['notebook'] = get_or_create_notebook(notebook_slug)
    elif notebook_slug:
        # Default to the notebook we're in
        payload['notebook'] = get_or_create_notebook(notebook_slug)

    if 'section' in payload:
        section_slug = payload['section']
        payload['section'] = get_or_create_section(section_slug, notebook_slug)
    else:
        if section_slug:
            # Section passed in
            payload['section'] = get_or_create_section(section_slug, notebook_slug)
        elif 'notebook' in payload and hasattr(payload['notebook'], 'default_section') and payload['notebook'].default_section is None:
            # Try the notebook's default section
            payload['section'] = payload['notebook'].default_section

    # Make sure there's a section or notebook
    if ('notebook' not in payload or payload['notebook'] is None) and ('section' not in payload or payload['section'] is None):
        return {
            'error': 'No notebook/section specified',
            'status': 400,
        }

    # See if it's an existing entry
    stripped_content = payload['content'].strip()

    if 'id' in payload and len(stripped_content) > 0:
        entry = models.Entry.objects.get(id=payload['id'])

        # Create new revision
        revision = models.Revision()
        revision.content = stripped_content
        revision.entry = entry
        revision.save()

        if 'title' in payload:
            entry.title = payload['title']
        else:
            entry.title = ''

        # Notebook and section
        entry.notebook = payload['notebook']
        if 'section' in payload and payload['section'] is not None:
            entry.section = payload['section']
        else:
            entry.section = None

        # Tags
        entry.tags.clear()
        if 'tags' in payload or 'tag' in payload:
            tags = [t.strip() for t in payload['tags'].split(',')]
            entry.tags.add(tags)

        # Update date
        if 'date' in payload:
            the_date = datetime.datetime.strptime(payload['date'], models.DATETIME_FORMAT)
            entry.date = the_date
            entry.save()

        e = serializers.EntrySerializer(entry)
        return e.data
    else:
        if len(stripped_content) > 0 and payload['notebook']:
            entry = models.Entry.objects.create(**payload)

            si.add_index(entry)
            e = serializers.EntrySerializer(entry)

            return e.data
        else:
            return {
                'error': 'No content to save or notebook is not specified',
                'status': 400,
            }


def add_payload_endpoint(request):
    callback = request.GET.get('callback', '')
    key = request.GET.get('key', '')

    if key != settings.VINCI_NON_REST_KEY:
        return JsonResponse({})

    response = add_payload(request)

    if callback and 'error' not in response:
        # Redirect to callback
        response = HttpResponse("", status=302)
        response['Location'] = callback
        return response
    else:
        # Return JSON response
        return JsonResponse(response)
