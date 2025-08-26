from django.contrib import admin
from .models import SuiviTuteurAdherent

@admin.register(SuiviTuteurAdherent)
class SuiviTuteurAdherentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'adherent',
        'tuteur',
        'statut',
        'date_creation',
    )
    list_filter = (
        'statut',
        'date_creation',
        'adherent',
        'tuteur',
    )
    search_fields = (
        'adherent__first_name',
        'adherent__last_name',
        'tuteur__first_name',
        'tuteur__last_name',
    )
    ordering = ('-date_creation',)
    list_per_page = 25

    fieldsets = (
        (None, {
            'fields': (
                'adherent',
                'tuteur',
                'statut',
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        Assure que la validation est toujours exécutée avant sauvegarde.
        """
        obj.full_clean()
        super().save_model(request, obj, form, change)
