from django.contrib import admin
from .models import Tuteur

@admin.register(Tuteur)
class TuteurAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'date_naissance',
        'sexe',
        'statut_user',
    )
    list_filter = (
        'sexe',
        'date_naissance',
        'statut_user',
    )
    search_fields = (
        'first_name',
        'last_name',
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
                'sexe',
                'adresse',
                'telephone',
                'email',
                'statut_user',
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        S'assure que le statut_user est toujours défini sur 'tuteur' si non renseigné.
        """
        if not obj.statut_user:
            obj.statut_user = "tuteur"
        super().save_model(request, obj, form, change)
