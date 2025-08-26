from django.contrib import admin
from .models import Activation

class ActivationAdmin(admin.ModelAdmin):
    list_display = ['key', 'activated_on', 'expires_on']  # Afficher la clé dans l'admin
    readonly_fields = ['key']  # Assurez-vous que la clé soit en lecture seule dans l'admin

admin.site.register(Activation, ActivationAdmin)
