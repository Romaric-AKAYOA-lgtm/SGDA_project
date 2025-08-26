from django.contrib import admin
from .models import Operation

@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_employe', 'type_operation', 'statut', 'date_debut', 'date_fin')
    list_filter = ('statut', 'type_operation')
    search_fields = ('id_employe__matricule', 'numero_note', 'numero_fiche')
    ordering = ('-date_creation',)
