from django.contrib import admin
from .models import Notebook, Entry, Revision, Group
from .models import Label, List, Card, Checklist, ChecklistItem


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


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ('title', 'color', 'order',)


@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    pass


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    pass


@admin.register(Checklist)
class ChecklistAdmin(admin.ModelAdmin):
    pass


@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    pass
