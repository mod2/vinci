from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Revision


class NotebookSlugField(serializers.RelatedField):
    def get_attribute(self, instance):
        try:
            return instance.entry.first().notebook
        except AttributeError:
            return instance

    def to_representation(self, value):
        return value.slug


class RevisionSerializer(serializers.ModelSerializer):
    notebook = NotebookSlugField(read_only=True)
    author = serializers.SlugRelatedField(slug_field='first_name',
                                          queryset=User.objects.all())

    class Meta:
        model = Revision
        fields = ('content', 'author', 'date', 'slug', 'title', 'notebook')
