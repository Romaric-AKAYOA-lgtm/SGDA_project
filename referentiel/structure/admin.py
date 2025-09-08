from django.contrib import admin
from .models import Structure

@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    # Champs affichés dans la liste
    list_display = (
        'raison_sociale',
        'matricule',
        'email',
        'telephone',
        'pays_residence',
        'devise_pays',
        'date_creation',
        'statut',
        'contact_personne',
    )

    # Champs recherchables
    search_fields = (
        'raison_sociale',
        'matricule',
        'email',
        'telephone',
        'contact_personne',
        'numero_enregistrement',
    )

    # Filtres latéraux
    list_filter = (
        'pays_residence',
        'devise_pays',
        'date_creation',
        'statut',
    )

    # Organisation des champs dans le formulaire d'administration
    fieldsets = (
        ('Informations Générales', {
            'fields': (
                'raison_sociale',
                'matricule',
                'date_creation',
                'structure_sous_tutelle',
                'direction_tutelle',
                'statut',
            )
        }),
        ('Contacts', {
            'fields': (
                'email',
                'telephone',
                'contact_personne',
                'adresse',
                'lieu_residence',
                'pays_residence',
                'devise_pays',
            )
        }),
        ('Identité visuelle', {
            'fields': (
                'logo_structure',
                'drapeau_pays',
            )
        }),
        ('Informations Complémentaires', {
            'fields': (
                'numero_enregistrement',
                'forme_juridique',
                'site_web',
                'domaines_activite',
                'zones_intervention',
            )
        }),
    )

    # Ordre par défaut
    ordering = ('raison_sociale',)
