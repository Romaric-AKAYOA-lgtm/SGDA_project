from django import forms
from .models import Unite

class UniteForm(forms.ModelForm):
    class Meta:
        model = Unite
        fields = ['designation', 'unite_parent']
        widgets = {
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'unite_parent': forms.Select(attrs={'class': 'form-select select2'}),  # <-- ici
        }
