from django.contrib import admin
from .models import Notebook, Entry, Revision


@admin.register(Notebook)
class NotebookAdmin(admin.ModelAdmin):
    pass


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    pass


@admin.register(Revision)
class RevisionAdmin(admin.ModelAdmin):
    pass
