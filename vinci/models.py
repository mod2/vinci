from django.db import models
from django.conf import settings
from django.shortcuts import resolve_url
from django_extensions.db.fields import AutoSlugField
from django.utils.text import slugify

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class Notebook(models.Model):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name', unique=True, editable=True)

    def __unicode__(self):
        return "{0.name} ({0.slug})".format(self)

    def get_absolute_url(self):
        return resolve_url('notebook', self.slug)


class Entry(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True, default='')
    slug = models.SlugField(null=True, blank=True)
    notebook = models.ForeignKey(Notebook, related_name='entries')
    date = models.DateTimeField(auto_now_add=True)

    @property
    def current_revision(self):
        return self.revisions.first()

    @property
    def content(self):
        return self.current_revision.content

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

    def __unicode__(self):
        return "entry: {}".format(self.current_revision)

    def save(self):
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

    def __unicode__(self):
        return "revision: {author} wrote '{content}'".format(
            author=self.author,
            content=self.content[:50],
        )

    class Meta:
        ordering = ['-last_modified']
