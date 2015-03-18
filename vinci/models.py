from django.db import models
from django.conf import settings
from django.shortcuts import resolve_url
from django_extensions.db.fields import AutoSlugField

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class Notebook(models.Model):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name', unique=True, editable=True)

    def __unicode__(self):
        return "{0.name} ({0.slug})".format(self)

    def get_absolute_url(self):
        return resolve_url('notebook', self.slug)


class Revision(models.Model):
    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=100)
    content = models.TextField()
    parent = models.ForeignKey('self', related_name='children',
                               null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               related_name='revisions')
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "revision: {title} by {author} - {content}".format(
            title=self.title,
            author=self.author,
            content=self.content[:50],
        )

    class Meta:
        ordering = ['-date']


class Entry(models.Model):
    current_revision = models.ForeignKey(Revision, related_name='entry')
    notebook = models.ForeignKey(Notebook, related_name='entries')
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "entry: {}".format(self.current_revision)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Entry'
        verbose_name_plural = 'Entries'
