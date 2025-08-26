from django.contrib import admin
from .models import Unite

@admin.register(Unite)
class UniteAdmin(admin.ModelAdmin):
    list_display = ('designation', 'unite_parent')
    search_fields = ('designation',)
