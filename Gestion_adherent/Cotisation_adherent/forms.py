from django import forms
from .models import Cotisation

class CotisationForm(forms.ModelForm):
    class Meta:
        model = Cotisation
        fields = [
            'adherent',
            'operation',
            'date_cotisation',
            'montant',
            'type_cotisation',
            'statut',
        ]

        widgets = {
            'adherent': forms.Select(attrs={
                'class': 'form-select select2',
                'placeholder': 'Sélectionner un adhérent'
            }),
            'operation': forms.Select(attrs={
                'class': 'form-select select2',
                'placeholder': 'Sélectionner une opération'
            }),
            'date_cotisation': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'montant': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'type_cotisation': forms.Select(attrs={
                'class': 'form-select'
            }),
            'statut': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def clean_montant(self):
        montant = self.cleaned_data.get('montant')
        if montant is None or montant <= 0:
            raise forms.ValidationError("Le montant doit être supérieur à 0.")
        return montant

    def clean(self):
        cleaned_data = super().clean()
        type_cotisation = cleaned_data.get('type_cotisation')
        statut = cleaned_data.get('statut')

        # Logique : si le type de cotisation correspond et est valide, le statut doit être 'valide'
        if type_cotisation and statut != 'valide':
            cleaned_data['statut'] = 'valide'

        return cleaned_data
