from rest_framework import serializers
# from django.contrib.auth.models import User
from .models import Entry, Notebook


class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ('title', 'slug', 'date', 'content', 'html')


class NotebookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notebook
        fields = ('name', 'slug')
