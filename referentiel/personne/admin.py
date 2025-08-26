from django.contrib import admin
from .models import Personne

@admin.register(Personne)
class PersonneAdmin(admin.ModelAdmin):
    model = Personne

    list_display = (
        'username',
        'first_name',
        'last_name',
        'matricule',
        'email',
        'telephone',
        'sexe',
        'nationalite',
        'situation_matrimoniale',
        'profession',
        'adresse',
        'statut',
        'statut_user',
        'date_creation',
    )

    readonly_fields = ('date_creation',)

    fieldsets = (
        (None, {
            'fields': (
                'username', 'password', 'first_name', 'last_name', 'email',
            ),
        }),
        ('Informations supplémentaires', {
            'fields': (
                'matricule',
                'date_naissance',
                'lieu_naissance',
                'sexe',
                'telephone',
                'nationalite',
                'situation_matrimoniale',
                'profession',
                'adresse',
                'image',
                'statut',
                'statut_user',
                'date_creation',
            ),
        }),
    )

    list_filter = ('date_creation', 'sexe', 'nationalite', 'statut', 'situation_matrimoniale')
    search_fields = ('username', 'matricule', 'email', 'telephone', 'first_name', 'last_name')
    ordering = ('-date_creation',)
