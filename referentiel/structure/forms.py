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
            'telephone',
            'matricule',
            'pays_residence',
            'devise_pays',
            'direction_tutelle',
            'structure_sous_tutelle',
            'logo_structure',
            'drapeau_pays',
            'lieu_residence',
            'numero_enregistrement',
            'forme_juridique',
            'site_web',
            'contact_personne',
            'domaines_activite',
            'zones_intervention',
            'statut',
        ]

        widgets = {
            'date_creation': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'raison_sociale': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'matricule': forms.TextInput(attrs={'class': 'form-control'}),
            'pays_residence': forms.TextInput(attrs={'class': 'form-control'}),
            'devise_pays': forms.TextInput(attrs={'class': 'form-control'}),
            'direction_tutelle': forms.TextInput(attrs={'class': 'form-control'}),
            'structure_sous_tutelle': forms.TextInput(attrs={'class': 'form-control'}),
            'lieu_residence': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_enregistrement': forms.TextInput(attrs={'class': 'form-control'}),
            'forme_juridique': forms.TextInput(attrs={'class': 'form-control'}),
            'site_web': forms.URLInput(attrs={'class': 'form-control'}),
            'contact_personne': forms.TextInput(attrs={'class': 'form-control'}),
            'domaines_activite': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'zones_intervention': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'statut': forms.Select(attrs={'class': 'form-control'}, choices=[('Actif', 'Actif'), ('Inactif', 'Inactif')]),
        }

    # Validation téléphone : uniquement chiffres
    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if telephone and not telephone.isdigit():
            raise forms.ValidationError("Le téléphone ne doit contenir que des chiffres.")
        return telephone

    # Validation date_creation obligatoire
    def clean_date_creation(self):
        date_creation = self.cleaned_data.get('date_creation')
        if not date_creation:
            raise forms.ValidationError("La date de création est obligatoire.")
        return date_creation

    # Validation email pour s'assurer qu'il est unique
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Structure.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Cet email est déjà utilisé par une autre structure.")
        return email
