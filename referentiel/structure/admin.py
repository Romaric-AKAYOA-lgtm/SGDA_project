from django.contrib import admin
from .models import Structure

@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    list_display = (
        'raison_sociale',
        'matricule',
        'email',
        'telephone',
        'pays_residence',
        'devise_pays',
        'date_creation',
    )
    search_fields = ('raison_sociale', 'matricule', 'email', 'telephone')
    list_filter = ('pays_residence', 'devise_pays', 'date_creation')
