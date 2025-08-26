from django.contrib import admin
from .models import Employe
from referentiel.personne.admin  import PersonneAdmin  # ou import direct selon ton organisation

@admin.register(Employe)
class EmployeAdmin(PersonneAdmin):
    model = Employe
    list_display = PersonneAdmin.list_display + ('grade', 'categorie')
    list_filter = PersonneAdmin.list_filter + ('grade', 'categorie')
    search_fields = PersonneAdmin.search_fields

    # Ajout propre des champs spécifiques sans doublons
    fieldsets = list(PersonneAdmin.fieldsets)
    fieldsets.append((
        'Informations Employé',
        {'fields': ('grade', 'categorie', 'echelle')}  # 👈 Ajout de "echelle"
    ))
