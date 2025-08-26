from django.contrib import admin
from .models import OrganisationUnite

@admin.register(OrganisationUnite)
class OrganisationUniteAdmin(admin.ModelAdmin):
    list_display = ('designation', 'date_creation', 'organisation_unite_parent', 'unite', 'structure')
    search_fields = ('designation',)
    list_filter = ('date_creation', 'structure', 'unite')
