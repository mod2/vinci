from django.contrib import admin
from .models import Notebook


@admin.register(Notebook)
class NotebookAdmin(admin.ModelAdmin):
    pass
