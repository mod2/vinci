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
    List of entries for the current notebook.
    """
    serializer_class = EntrySerializer


class EntryDetailAPIView(NotebookLimitMixin, APIView):
    """
    # Entry
    A single entry detail
    """
    serializer_class = EntrySerializer

    def get(self, notebook_slug, slug):
        entry = (Entry.objects
                 .from_slug(slug)
                 .filter(notebook__slug=notebook_slug)
                 .first()
                 )
        return APIResponse(self.serializer_class(entry))


class NotebookListAPIView(ListCreateAPIView):
    """
    # Notebooks
    List of all the notebooks.
    """
    serializer_class = NotebookSerializer
    queryset = Notebook.objects.all()
