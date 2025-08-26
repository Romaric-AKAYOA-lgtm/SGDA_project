from django import forms
from .models import Fonction

class FonctionForm(forms.ModelForm):
    class Meta:
        model = Fonction
        fields = ['designation', 'fonction_parent', 'structure']
        widgets = {
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'fonction_parent': forms.Select(attrs={'class': 'form-select'}),
            'structure': forms.Select(attrs={'class': 'form-select'}),
        }
