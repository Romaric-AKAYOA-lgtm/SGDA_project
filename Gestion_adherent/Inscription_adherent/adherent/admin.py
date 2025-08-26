from django.contrib import admin
from .models import Adherent

@admin.register(Adherent)
class AdherentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'date_naissance',
        'pere',
        'mere',
        'statut_user',
    )
    list_filter = (
        'date_naissance',
        'statut_user',
        'pere',
        'mere',
    )
    search_fields = (
        'first_name',
        'last_name',
        'pere__first_name',
        'pere__last_name',
        'mere__first_name',
        'mere__last_name',
    )
    ordering = ('last_name', 'first_name')
    list_per_page = 25

    fieldsets = (
        (None, {
            'fields': (
                'first_name',
                'last_name',
                'date_naissance',
                'lieu_naissance',
                'adresse',
                'telephone',
                'email',
                'pere',
                'mere',
                'statut_user',
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        S'assure que la validation custom (clean) est appliquée avant l'enregistrement.
        """
        obj.full_clean()
        super().save_model(request, obj, form, change)
