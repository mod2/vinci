from django.shortcuts import get_object_or_404
from rest_framework.response import Response as APIResponse
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from vinci.serializers import EntrySerializer, NotebookSerializer
from vinci.models import Entry, Notebook


class NotebookLimitMixin(object):
    def get_queryset(self):
        notebook_slug = self.kwargs.get('notebook_slug', '')
        return Entry.objects.filter(notebook__slug=notebook_slug)


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
        if content:
            kwargs = {'content': content,
                      'author': request.user,
                      'notebook': notebook,
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

    def _get_args(self, args, kwargs):
        notebook_slug = kwargs.get('notebook_slug')
        slug = kwargs.get('slug')

        if notebook_slug is None and len(args) > 0:
            notebook_slug = args[0]
        elif notebook_slug is None:
            notebook_slug = ''

        if slug is None and len(args) > 1:
            slug = args[1]
        elif slug is None:
            slug = ''

        return (notebook_slug, slug)

    def get(self, request, *args, **kwargs):
        notebook_slug, slug = self._get_args(args, kwargs)
        print("{} - {}".format(notebook_slug, slug))
        entry = (Entry.objects
                 .from_slug(slug)
                 .filter(notebook__slug=notebook_slug)
                 .first()
                 )
        return APIResponse(self.serializer_class(entry).data)

    def put(self, request):
        pass


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
