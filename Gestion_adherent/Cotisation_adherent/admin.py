from django.contrib import admin
from .models import Cotisation

@admin.register(Cotisation)
class CotisationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'adherent',
        'operation',
        'date_cotisation',
        'montant',
        'statut',
        'type_cotisation',
    )
    list_filter = (
        'statut',
        'type_cotisation',
        'date_cotisation',
    )
    search_fields = (
        'adherent__first_name',
        'adherent__last_name',
        'operation__id',
    )
    ordering = ('-date_cotisation',)
    list_per_page = 25

    fieldsets = (
        (None, {
            'fields': (
                'adherent',
                'operation',
                'date_cotisation',
                'montant',
                'statut',
                'type_cotisation',
            )
        }),
    )

    readonly_fields = ('statut',)  # le statut est calculé automatiquement

    def save_model(self, request, obj, form, change):
        """
        Appelle la méthode save du modèle pour que le statut se mette à jour automatiquement.
        """
        obj.save()
        super().save_model(request, obj, form, change)
