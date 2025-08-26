from django import forms
from .models import Structure

class StructureForm(forms.ModelForm):
    class Meta:
        model = Structure
        fields = [
            'raison_sociale',
            'date_creation',
            'adresse',
            'email',
            'pays_residence',
            'devise_pays',
            'direction_tutelle',
            'structure_sous_tutelle',  # Champ ajouté
            'telephone',
            'matricule',
            'logo_structure',
            'drapeau_pays',
            'lieu_residence',
        ]
        widgets = {
            'date_creation': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'raison_sociale': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'pays_residence': forms.TextInput(attrs={'class': 'form-control'}),
            'devise_pays': forms.TextInput(attrs={'class': 'form-control'}),
            'direction_tutelle': forms.TextInput(attrs={'class': 'form-control'}),
            'structure_sous_tutelle': forms.TextInput(attrs={'class': 'form-control'}),  # Widget ajouté
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'matricule': forms.TextInput(attrs={'class': 'form-control'}),
            'lieu_residence': forms.TextInput(attrs={'class': 'form-control'}),
        }

        """      
    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if telephone and not telephone.isdigit():
            raise forms.ValidationError("Le téléphone ne doit contenir que des chiffres.")
        return telephone
        """
    def clean_date_creation(self):
        date_creation = self.cleaned_data.get('date_creation')
        if date_creation is None:
            raise forms.ValidationError("La date de création est obligatoire.")
        return date_creation
