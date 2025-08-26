from django.contrib import admin
from .models import Fonction

@admin.register(Fonction)
class FonctionAdmin(admin.ModelAdmin):
    list_display = ('designation', 'fonction_parent', 'structure')
    search_fields = ('designation',)
    list_filter = ('structure',)
