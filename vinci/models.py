from django.db import models
from django.conf import settings
from django.shortcuts import resolve_url
from django_extensions.db.fields import AutoSlugField
from django.utils.text import slugify
from model_utils import Choices

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
    def from_slug(self, slug, notebook_slug):
        # See if it's a post ID or a page slug
        try:
            slug_id = int(slug)
        except:
            slug_id = 0

        # Filter by entries with this id/slug for this notebook
        entry = self.filter(models.Q(notebook__slug=notebook_slug)
                            & models.Q(slug=slug)
                            | models.Q(pk=slug_id)).first()

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

        entry = super().create(**kwargs)

        revision = Revision()
        revision.content = content
        revision.author = user
        revision.entry = entry
        revision.save()

        # Update dates
        if 'date' in kwargs:
            revision.last_modified = kwargs['date']
            revision.save()
            entry.date = kwargs['date']
            entry.save()

        return entry


class Notebook(models.Model):
    STATUS = Choices(
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('deleted', 'Deleted'),
    )

    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name', unique=True, editable=True)
    status = models.CharField(max_length=20,
                              default=STATUS.active,
                              choices=STATUS)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               related_name='notebooks')

    objects = NotebookManager()

    def __str__(self):
        return "{0.name}".format(self)

    def get_absolute_url(self):
        return resolve_url('notebook', self.slug)


class Entry(models.Model):
    title = models.CharField(max_length=100, blank=True, default='')
    slug = models.SlugField(blank=True, default='')
    notebook = models.ForeignKey(Notebook, related_name='entries')
    date = models.DateTimeField(auto_now_add=True)

    objects = EntryQuerySet.as_manager()

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
        return resolve_url('entry', self.notebook.slug, slug)

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

    def __str__(self):
        return "{content}".format(content=self.content_excerpt())

    class Meta:
        ordering = ['-last_modified']
