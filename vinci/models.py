from django.db import models
from django.conf import settings

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class Notebook(models.Model):
    slug = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True)

    # def set_slug(self):
    #     slug = utils.slugify(self.name)
    #     num = Notebook.select().where(
    #         p.fn.Substr(Notebook.slug, 1, len(slug)) == slug).count()
    #     if num > 0:
    #         slug += '-' + str(num)
    #     self.slug = slug


class Revision(models.Model):
    content = models.TextField()
    parent = models.ForeignKey('self', related_name='children', null=True)
    title = models.TextField()
    slug = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               related_name='revisions')
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']


class Entry(models.Model):
    current_revision = models.ForeignKey(Revision, null=True, default=None)
    notebook = models.ForeignKey(Notebook, related_name='entries')
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def serialize(self):
        entry = {}
        entry['content'] = self.current_revision.content
        entry['notebook'] = self.notebook.slug
        entry['author'] = self.author.display
        entry['date'] = self.date.strftime(DATETIME_FORMAT)
        entry['last_modified'] = self.last_modified.strftime(DATETIME_FORMAT)
        return entry
