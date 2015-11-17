from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import resolve_url
from django_extensions.db.fields import AutoSlugField
from django.utils.text import slugify
from model_utils import Choices
from taggit.managers import TaggableManager
from django.utils.timezone import localtime

import datetime

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# User Profile model

class UserPrefs(models.Model):
    user = models.OneToOneField(User, related_name="prefs", primary_key=True)

    class Meta:
        ordering = ['user']


# Custom Managers and QuerySets

class StatusQueries(models.QuerySet):
    def active(self):
        return self.filter(status='active')

    def archived(self):
        return self.filter(status='archived')

    def deleted(self):
        return self.filter(status='deleted')


class NotebookManager(StatusQueries, models.QuerySet):
    pass


class SectionManager(StatusQueries, models.QuerySet):
    pass


class EntryQuerySet(StatusQueries, models.QuerySet):
    def from_slug(self, slug, section_slug=None, notebook_slug=None):
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

        # If there's a section slug, filter by it
        if section_slug:
            entries = entries.filter(section__slug=section_slug)

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
            tags = kwargs.pop('tags')
        except KeyError:
            tags = ''

        entry = super().create(**kwargs)

        revision = Revision()
        revision.content = content
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
            the_date = datetime.datetime.strptime(kwargs['date'], DATETIME_FORMAT)
            revision.last_modified = the_date
            revision.save()
            entry.date = the_date
            entry.save()

        return entry


# Vinci Models

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

    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name', unique=True, editable=True)
    status = models.CharField(max_length=20,
                              default=STATUS.active,
                              choices=STATUS)
    group = models.ForeignKey(Group, related_name="notebooks", default=None,
                              null=True, blank=True)

    default_section = models.ForeignKey("Section", related_name="default_notebooks", blank=True, null=True)

    default_mode = models.CharField(max_length=30, blank=True, null=True)

    dotfile = models.TextField(blank=True, null=True)
    custom_css = models.TextField(blank=True, null=True)

    objects = NotebookManager.as_manager()

    def __str__(self):
        return "{}".format(self.slug)

    def get_absolute_url(self):
        return resolve_url('notebook', self.slug)

    def delete(self):
        self.status = self.STATUS.deleted
        self.save()


class Section(models.Model):
    STATUS = Choices(
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('deleted', 'Deleted'),
    )

    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, default='')

    status = models.CharField(max_length=20,
                              default=STATUS.active,
                              choices=STATUS)

    notebook = models.ForeignKey(Notebook, related_name='sections')

    default_mode = models.CharField(max_length=30, blank=True, null=True)

    objects = SectionManager.as_manager()

    def __str__(self):
        return "{}/{}".format(self.notebook.slug, self.slug)

    def get_absolute_url(self):
        return resolve_url('notebook_section', self.notebook.slug, self.slug)


class Entry(models.Model):
    STATUS = Choices(
        ('active', 'Active'),
        ('deleted', 'Deleted'),
    )

    title = models.CharField(max_length=100, blank=True, default='')
    slug = models.SlugField(blank=True, default='')
    notebook = models.ForeignKey(Notebook, related_name='entries')
    section = models.ForeignKey(Section, related_name='entries', null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20,
                              default=STATUS.active,
                              choices=STATUS)
    last_modified = models.DateTimeField(null=True, blank=True, default=None)

    objects = EntryQuerySet.as_manager()
    tags = TaggableManager(blank=True)

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
        r = Revision(content=value, entry=self, parent=cr)
        r.save()

    def first_line(self):
        return self.content.split('\n')[0]

    def second_line(self):
        lines = self.content.split('\n')[1:]

        for line in lines:
            if line.strip():
                return line

        return ''

    def get_payload(self):
        if self.current_revision:
            return self.current_revision.get_payload()
        else:
            return ''

    def html(self):
        content = self.content

        for plugin_name in settings.VINCI_PLUGINS:
            plugins = __import__("plugins", fromlist=[plugin_name])
            plugin = getattr(plugins, plugin_name)
            content = plugin.process(content,
                                        self,
                                        self.notebook.get_absolute_url())

        return content

    def unparsed_html(self):
        content = self.content
        content = content.replace('\n', '<br>')
        content = content.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
        content = content.replace('    ', '&nbsp;&nbsp;&nbsp;&nbsp;')

        return content

    def get_absolute_url(self):
        slug = self.id

        if self.section:
            section_slug = self.section.slug

            # For wiki pages, use the slug, otherwise
            if self.slug and self.section.default_mode == 'wiki':
                slug = self.slug
        else:
            section_slug = '--'

        return resolve_url('entry', self.notebook.slug, section_slug, slug)

    def __str__(self):
        return "{}".format(self.current_revision)

    def save(self, **kwargs):
        if self.title:
            self.slug = slugify(self.title)

        super(Entry, self).save()

    def delete(self):
        self.status = self.STATUS.deleted
        self.save()

    class Meta:
        ordering = ['-date']
        verbose_name = 'Entry'
        verbose_name_plural = 'Entries'


class Revision(models.Model):
    content = models.TextField()
    entry = models.ForeignKey(Entry, related_name='revisions')
    parent = models.ForeignKey('self', related_name='children',
                               null=True, blank=True)
    last_modified = models.DateTimeField(auto_now_add=True)

    def save(self):
        parent = self.entry.current_revision
        self.parent = parent
        super(Revision, self).save()
        self.entry.last_modified = self.last_modified
        self.entry.save()

    def content_excerpt(self):
        return self.content[:60]

    def get_payload(self):
        content = self.content

        content += '\n\n'

        # ::notebook/section
        content += '::{}'.format(self.entry.notebook.slug)
        if self.entry.section:
            content += '/{}'.format(self.entry.section.slug)
        content += '\n'

        # :title Title
        if self.entry.title:
            content += ':title {}\n'.format(self.entry.title)

        # :date 2013-10-10 09:09:10
        entry_date = localtime(self.entry.date) # convert to local time
        content += ':date {}\n'.format(str(entry_date)[:19])

        # :tags one-tag, two-tag
        if len(self.entry.tags.all()):
            content += ':tags {}\n'.format(', '.join([str(tag) for tag in self.entry.tags.all()]))

        # :id 2930
        content += ':id {}'.format(self.entry.id)

        return content.strip()

    def html(self):
        content = self.content

        for plugin_name in settings.VINCI_PLUGINS:
            plugins = __import__("plugins", fromlist=[plugin_name])
            plugin = getattr(plugins, plugin_name)
            content = plugin.process(content,
                                        self.entry,
                                        self.entry.notebook.get_absolute_url())

        return content

    def unparsed_html(self):
        content = self.content
        content = content.replace('\n', '<br>')
        content = content.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
        content = content.replace('    ', '&nbsp;&nbsp;&nbsp;&nbsp;')

        return content

    def __str__(self):
        return "{content}".format(content=self.content_excerpt())

    class Meta:
        ordering = ['-last_modified']
