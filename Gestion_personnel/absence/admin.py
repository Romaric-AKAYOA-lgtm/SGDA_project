from django.contrib import admin
from .models import Absence

@admin.register(Absence)
class AbsenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_absence', 'statut', 'date_debut', 'duree', 'date_retour', 'lieu')
    list_filter = ('type_absence', 'statut')
    search_fields = ('lieu', 'motif')
    ordering = ('-date_creation',)
