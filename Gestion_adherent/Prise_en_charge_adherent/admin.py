from django.contrib import admin
from .models import PriseEnChargeAdherent

@admin.register(PriseEnChargeAdherent)
class PriseEnChargeAdherentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'objet',
        'adherent',
        'date_creation',
        'nom_complet_medecin',
        'fonction_medecin',
        'operation_enregistrer',
        'operation_medecin',
    )
    list_filter = (
        'date_creation',
        'operation_medecin',
    )
    search_fields = (
        'objet',
        'adherent__first_name',
        'adherent__last_name',
        'nom_complet_medecin',
    )
    ordering = ('-date_creation',)
    list_per_page = 25

    fieldsets = (
        (None, {
            'fields': (
                'objet',
                'description',
                'date_creation',
                'adherent',
                'operation_enregistrer',
                'operation_medecin',
                'nom_complet_medecin',
                'fonction_medecin',
                'specialite_medecin',
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        Appelle la méthode save du modèle pour appliquer la logique de validation
        du médecin si operation_medecin n'est pas renseignée.
        """
        obj.save()
        super().save_model(request, obj, form, change)
