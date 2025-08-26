from django import forms
from .models import OrganisationUnite

class OrganisationUniteForm(forms.ModelForm):
    class Meta:
        model = OrganisationUnite
        fields = [
            'designation',
            'organisation_unite_parent',
            'unite',
            'structure'
        ]
        widgets = {
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'organisation_unite_parent': forms.Select(attrs={'class': 'form-select'}),
            'unite': forms.Select(attrs={'class': 'form-select'}),
            'structure': forms.Select(attrs={'class': 'form-select'}),
        }
