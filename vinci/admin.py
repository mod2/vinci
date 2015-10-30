from django.contrib import admin
from .models import Notebook, Section, Entry, Revision, Group


class RevisionInline(admin.StackedInline):
    model = Revision
    fields = ('content', 'entry', 'parent', 'author',)
    extra = 1

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        return self.extra


@admin.register(Notebook)
class NotebookAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    pass


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    pass


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    pass


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('date', 'notebook', 'current_revision', 'title', 'slug',)
    inlines = [RevisionInline]
    pass


@admin.register(Revision)
class RevisionAdmin(admin.ModelAdmin):
    list_display = ('last_modified', 'content_excerpt', 'parent', 'author',)
    pass

