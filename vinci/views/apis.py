from rest_framework.views import APIView
from rest_framework.response import Response as APIResponse
from rest_framework import generics
from vinci.serializers import RevisionSerializer
from vinci.models import Revision, Entry, Notebook


class CreateEntryAPI(APIView):
    def get(self, request, slug):
        data = {}
        data['content'] = request.GET.get('content')
        data['author'] = request.GET.get('author')
        data['slug'] = request.GET.get('slug')
        data['title'] = request.GET.get('title')
        return APIResponse(self.create(slug, data))

    def post(self, request, slug):
        pass

    def create(self, notebook_slug, data):
        r = RevisionSerializer(data=data)
        if r.is_valid():
            rev = r.save()
            e = Entry()
            e.current_revision = rev
            e.notebook = Notebook.objects.get(slug=notebook_slug)
            e.save()
            return r.data
        else:
            return r.errors


class EntryAPI(generics.ListCreateAPIView):
    serializer_class = RevisionSerializer
    queryset = Revision.objects.all()
