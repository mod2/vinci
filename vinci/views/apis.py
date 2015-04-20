from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from rest_framework.response import Response as APIResponse
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from vinci.serializers import EntrySerializer, NotebookSerializer
from vinci.models import Entry, Notebook, Revision, DATETIME_FORMAT
from django.http import JsonResponse

import datetime


class APIResponseNotFound(APIResponse):
    def __init__(self, message='Not Found', **kwargs):
        detail = {'detail': message}
        super().__init__(data=detail, status=404, **kwargs)


class NotebookLimitMixin(object):
    def get_queryset(self):
        qs = Entry.objects.all()
        notebook_slug = self.kwargs.get('notebook_slug', '')
        if notebook_slug:
            qs = qs.filter(notebook__slug=notebook_slug)
        return qs


class EntryListAPIView(NotebookLimitMixin, ListCreateAPIView):
    """
    # Entries
    - **GET** List the entries for the current notebook.
    - **POST** Create a new entry attached to the current notebook.
    - **PUT** Edit the current notebooks name or status.
    - **DELETE** Delete the current notebook (sets the status to deleted).
    """
    serializer_class = EntrySerializer

    def post(self, request, notebook_slug):
        notebook = get_object_or_404(Notebook, slug=notebook_slug)
        content = request.data.get('content')
        title = request.data.get('title', '')
        tags = request.data.get('tags')
        if content:
            kwargs = {'content': content,
                      'author': request.user,
                      'notebook': notebook,
                      'title': title,
                      'tags': tags,
                      }
            entry = Entry.objects.create(**kwargs)
            e = EntrySerializer(entry)
            return APIResponse(e.data)
        return APIResponse({'detail': 'No content to save.'}, status=400)

    def put(self, request, notebook_slug):
        notebook = get_object_or_404(Notebook, slug=notebook_slug)
        name = request.data.get('name')
        status = request.data.get('status')
        changed = False
        if name is not None:
            notebook.name = name
            changed = True
        if status is not None and status in Notebook.STATUS:
            notebook.status = status
            changed = True
        if changed:
            notebook.save()
        nb = NotebookSerializer(notebook, context={'request': request})
        return APIResponse(nb.data)

    def delete(self, request, notebook_slug):
        notebook = get_object_or_404(Notebook, slug=notebook_slug)
        notebook.status = notebook.STATUS.deleted
        nb = NotebookSerializer(notebook, context={'request': request})
        notebook.save()
        return APIResponse(nb.data)


class EntryDetailAPIView(NotebookLimitMixin, APIView):
    """
    # Entry
    A single entry detail
    """
    serializer_class = EntrySerializer

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
            except Entry.DoesNotExist:
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
        entry = self.get_entry_for_request()
        content = request.data.get('content')
        tags = [t.strip() for t in request.data.get('tags', '').split(',')]
        date = request.data.get('date', '')
        if entry:
            entry.content = content
            entry.title = request.data.get('title', '')
            entry.date = datetime.datetime.strptime(date, DATETIME_FORMAT)
            entry.save()
            entry.tags.set(*tags)
            e = self.serializer_class(entry).data
            return APIResponse(e)
        else:
            return APIResponseNotFound('No entry found.')

    def delete(self, request, *args, **kwargs):
        entry = self.get_entry_for_request()
        if entry:
            e = self.serializer_class(entry).data
            entry.delete()
            return APIResponse(e)
        else:
            return APIResponseNotFound('No entry found.')


class NotebookListAPIView(ListCreateAPIView):
    """
    # Notebooks
    List of all the notebooks.

    ## Optional Parameters

    * `status` - active (default), archived, deleted

    ## Examples

    * `GET /api/?status=archived` Return list of all the archived notebooks.
    """
    serializer_class = NotebookSerializer

    def get_queryset(self):
        qs = Notebook.objects
        status = self.request.GET.get('status', Notebook.STATUS.active)
        if status == Notebook.STATUS.archived:
            qs = qs.archived()
        elif status == Notebook.STATUS.deleted:
            qs = qs.deleted()
        else:  # show active
            qs = qs.active()
        return qs

    def post(self, request):
        data = {'name': request.data.get('name'),
                'author': request.user,
                }
        notebook = Notebook.objects.create(**data)
        n = NotebookSerializer(notebook, context={'request': request})
        return APIResponse(n.data)


if settings.VINCI_ENABLE_NON_REST_APIS:
    def append_today(request, notebook_slug):
        """ Appends to today's entry, creating it if it's not there. """

        callback = request.GET.get('callback', '')
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
            notebook = Notebook.objects.get(slug=notebook_slug)

            # Get first entry for today
            results = Entry.objects.filter(notebook=notebook,
                                           date__range=[today, tomorrow],
                                           ).order_by('date')[:1]

            if len(results) > 0:
                entry = results[0]
            else:
                # We don't have an entry today, so create it (strip it first
                # so there's no initial newline)

                kwargs = {'content': content.strip(),
                          'author': request.user,
                          'notebook': notebook,
                          }
                entry = Entry.objects.create(**kwargs)

            # Get the text
            cur_rev = entry.current_revision

            # Add new revision with appended content
            new_revision = Revision()
            new_revision.entry = entry
            new_revision.content = cur_rev.content + '\n\n' + content
            new_revision.author = notebook.author
            new_revision.parent = cur_rev
            new_revision.save()

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
            return redirect(callback)
        else:
            # Return JSON response
            return JsonResponse(response)

    def add_entry(request, notebook_slug):
        """ Adds an entry to a notebook. """

        callback = request.GET.get('callback', '')
        key = request.GET.get('key', '')

        if key != settings.VINCI_NON_REST_KEY:
            return JsonResponse({})

        if request.method == 'GET':
            content = request.GET.get('content')
        elif request.method == 'POST':
            content = request.POST.get('content')

        # Create the entry
        try:
            # Notebook
            notebook = Notebook.objects.get(slug=notebook_slug)

            kwargs = {'content': content.strip(),
                      'author': notebook.author,
                      'notebook': notebook,
                      }
            entry = Entry.objects.create(**kwargs)

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
            return redirect(callback)
        else:
            # Return JSON response
            return JsonResponse(response)
