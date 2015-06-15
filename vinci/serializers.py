from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Entry, Notebook, Label, List, Card, Checklist, ChecklistItem


class NotebookSerializer(serializers.ModelSerializer):
    entries = serializers.HyperlinkedIdentityField(
        view_name='api_entry_list', lookup_field='slug',
        lookup_url_kwarg='notebook_slug')

    class Meta:
        model = Notebook
        fields = ('name',
                  'slug',
                  'status',
                  'group',
                  'default_section',
                  'display_logs',
                  'display_notes',
                  'display_pages',
                  'display_journals',
                  'condense_notes',
                  'parse_notes',
                  'author',
                  'entries',
                  )


class RevisionField(serializers.CharField):
    def get_attribute(self, instance):
        self.instance = instance
        return instance

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        revision = value.current_revision
        try:
            return getattr(revision, self.field_name)
        except AttributeError:
            return ''


class ContentField(RevisionField):
    field_name = 'content'


class AuthorField(RevisionField):
    field_name = 'author'

    def to_representation(self, value):
        value = super(AuthorField, self).to_representation(value)
        if isinstance(value, User):
            return {'username': value.username,
                    'name': ("{0.first_name} {0.last_name}"
                             .format(value)
                             .strip()
                             ),
                    }
        else:
            return value

    def to_internal_value(self, value):
        return User.objects.get(username=value)


class EntrySerializer(serializers.ModelSerializer):
    notebook = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=Notebook.objects.active())
    content = ContentField()
    author = AuthorField(required=False)

    def create(self, kwargs):
        return Entry.objects.create(**kwargs)

    class Meta:
        model = Entry
        fields = ('id', 'title', 'slug', 'date', 'content', 'author',
                  'html', 'notebook')


# Todo board model serializers
class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        exclude = ()


class ListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='list-detail')
    notebook = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=Notebook.objects.active())

    class Meta:
        model = List
        exclude = ()


class CardSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='card-detail')

    class Meta:
        model = Card
        exclude = ()


class ChecklistSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='checklist-detail')

    class Meta:
        model = Checklist
        exclude = ()


class ChecklistItemSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='checklistitem-detail')

    class Meta:
        model = ChecklistItem
        exclude = ()
