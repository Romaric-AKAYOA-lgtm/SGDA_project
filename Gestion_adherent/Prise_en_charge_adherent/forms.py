from django import forms
from .models import PriseEnChargeAdherent

class PriseEnChargeAdherentForm(forms.ModelForm):
    class Meta:
        model = PriseEnChargeAdherent
        fields = [
            'objet', 'description', 'date_creation',
            'nom_complet_medecin', 'fonction_medecin', 'specialite_medecin',
            'adherent',  'operation_medecin', 'operation_enregistrer',
        ]
        widgets = {
            'date_creation': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'objet': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'nom_complet_medecin': forms.TextInput(attrs={'class': 'form-control'}),
            'fonction_medecin': forms.TextInput(attrs={'class': 'form-control'}),
            'specialite_medecin': forms.TextInput(attrs={'class': 'form-control'}),
            'adherent': forms.Select(attrs={'class': 'form-select'}),
            'operation_medecin': forms.Select(attrs={'class': 'form-select'}),
            'operation_enregistrer': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'date_creation': "Date de création",
            'objet': "Objet",
            'description': "Description",
            'nom_complet_medecin': "Nom complet du médecin",
            'fonction_medecin': "Fonction du médecin",
            'specialite_medecin': "Spécialité du médecin",
            'adherent': "Adhérent",
            'operation_medecin': "Médecin",
            'operation_enregistrer': "Enregistreur",
        }
    def clean(self):
        cleaned_data = super().clean()
        operation_medecin = cleaned_data.get('operation_medecin')
        nom_complet_medecin = cleaned_data.get('nom_complet_medecin')
        fonction_medecin = cleaned_data.get('fonction_medecin')

        # Validation : si pas d'opération médecin, nom et fonction doivent être renseignés
        if not operation_medecin:
            if not nom_complet_medecin or not fonction_medecin:
                raise forms.ValidationError(
                    "Si l'opération médecin n'est pas renseignée, le nom complet et la fonction du médecin doivent être fournis."
                )

        return cleaned_data
