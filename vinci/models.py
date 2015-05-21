from django.db import models
from django.conf import settings
from django.shortcuts import resolve_url
from django_extensions.db.fields import AutoSlugField
from django.utils.text import slugify
from model_utils import Choices
from taggit.managers import TaggableManager

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class NotebookManager(models.Manager):
    def active(self):
        qs = self.get_queryset()
        return qs.filter(status='active')

    def archived(self):
        qs = self.get_queryset()
        return qs.filter(status='archived')

    def deleted(self):
        qs = self.get_queryset()
        return qs.filter(status='deleted')


class EntryQuerySet(models.QuerySet):
    def from_slug(self, slug, notebook_slug=None):
        # See if it's a post ID or a page slug
        try:
            slug_id = int(slug)
        except:
            slug_id = 0

        # Filter by entries with this id/slug for this notebook
        entries = self.filter(models.Q(slug=slug)
                              | models.Q(pk=slug_id))

        # If there's a notebook slug, filter by it
        if notebook_slug:
            entries = entries.filter(notebook__slug=notebook_slug)

        # Get the first entry
        entry = entries.first()

        if not entry:
            raise Entry.DoesNotExist('No entry with slug ({}) or id ({}).'
                                     .format(slug, slug_id))

        return entry

    def create(self, **kwargs):
        try:
            content = kwargs.pop('content')
        except KeyError:
            content = ''

        try:
            user = kwargs.pop('author')
        except KeyError:
            user = ''

        try:
            tags = kwargs.pop('tags')
        except KeyError:
            tags = ''

        entry = super().create(**kwargs)

        revision = Revision()
        revision.content = content
        revision.author = user
        revision.entry = entry
        revision.save()

        if tags:
            tags = [t.strip() for t in tags.split(',')]
            entry.tags.add(tags)
        else:
            # No tags, so clear it
            entry.tags.clear()

        # Update dates
        if 'date' in kwargs:
            revision.last_modified = kwargs['date']
            revision.save()
            entry.date = kwargs['date']
            entry.save()

        return entry


class Group(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def active_notebooks(self):
        return self.notebooks.active().order_by('name')

    class Meta:
        ordering = ['name']


class Notebook(models.Model):
    STATUS = Choices(
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('deleted', 'Deleted'),
    )

    ENTRY_TYPE = Choices(
        ('log', 'Log'),
        ('note', 'Note'),
        ('page', 'Page'),
        ('journal', 'Journal'),
    )

    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name', unique=True, editable=True)
    status = models.CharField(max_length=20,
                              default=STATUS.active,
                              choices=STATUS)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               related_name='notebooks')
    group = models.ForeignKey(Group, related_name="notebooks", default=None,
                              null=True)

    default_section = models.CharField(max_length=20,
                                       default=ENTRY_TYPE.log,
                                       choices=ENTRY_TYPE)
    display_logs = models.BooleanField(default=True)
    display_notes = models.BooleanField(default=True)
    display_pages = models.BooleanField(default=True)
    display_journals = models.BooleanField(default=False)

    objects = NotebookManager()

    def __str__(self):
        return "{0.name}".format(self)

    def get_absolute_url(self):
        return resolve_url('notebook', self.slug)


class Entry(models.Model):
    ENTRY_TYPE = Choices(
        ('log', 'Log'),
        ('note', 'Note'),
        ('page', 'Page'),
    )

    title = models.CharField(max_length=100, blank=True, default='')
    slug = models.SlugField(blank=True, default='')
    notebook = models.ForeignKey(Notebook, related_name='entries')
    date = models.DateTimeField(auto_now_add=True)
    entry_type = models.CharField(max_length=20,
                                  default=ENTRY_TYPE.log,
                                  choices=ENTRY_TYPE)

    objects = EntryQuerySet.as_manager()
    tags = TaggableManager()

    @property
    def current_revision(self):
        return self.revisions.first()

    @property
    def content(self):
        revision = self.current_revision
        return '' if not revision else revision.content

    @content.setter
    def content(self, value):
        cr = self.current_revision
        r = Revision(content=value, entry=self, parent=cr, author=cr.author)
        r.save()

    def html(self):
        content = self.content
        for plugin_name in settings.VINCI_PLUGINS:
            plugins = __import__("plugins", fromlist=[plugin_name])
            plugin = getattr(plugins, plugin_name)
            content = plugin.process(content,
                                     self,
                                     self.notebook.get_absolute_url())
        return content

    def get_absolute_url(self):
        slug = self.id
        if self.slug:
            slug = self.slug
        return resolve_url('entry', self.notebook.slug, self.entry_type, slug)

    def get_possible_types(self):
        """ Returns list of possible types for this notebook. """

        # TODO: make this more elegant

        possible_types = []

        if self.notebook.display_logs:
            possible_types.append({ 'value': 'log', 'label': 'Log' })
        if self.notebook.display_notes:
            possible_types.append({ 'value': 'note', 'label': 'Note' })
        if self.notebook.display_pages:
            possible_types.append({ 'value': 'page', 'label': 'Page' })
        if self.notebook.display_journals:
            possible_types.append({ 'value': 'journal', 'label': 'Journal' })

        return possible_types

    def __str__(self):
        return "{}".format(self.current_revision)

    def save(self, **kwargs):
        if self.title:
            self.slug = slugify(self.title)
        super(Entry, self).save()

    class Meta:
        ordering = ['-date']
        verbose_name = 'Entry'
        verbose_name_plural = 'Entries'


class Revision(models.Model):
    content = models.TextField()
    entry = models.ForeignKey(Entry, related_name='revisions')
    parent = models.ForeignKey('self', related_name='children',
                               null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               related_name='revisions')
    last_modified = models.DateTimeField(auto_now_add=True)

    def save(self):
        parent = self.entry.current_revision
        self.parent = parent
        super(Revision, self).save()

    def content_excerpt(self):
        return self.content[:60]

    def html(self):
        content = self.content
        for plugin_name in settings.VINCI_PLUGINS:
            plugins = __import__("plugins", fromlist=[plugin_name])
            plugin = getattr(plugins, plugin_name)
            content = plugin.process(content,
                                     self.entry,
                                     self.entry.notebook.get_absolute_url())
        return content

    def __str__(self):
        return "{content}".format(content=self.content_excerpt())

    class Meta:
        ordering = ['-last_modified']
