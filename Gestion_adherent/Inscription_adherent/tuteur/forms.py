from django import forms
from .models import Tuteur
from referentiel.personne.forms import PersonneForm
from datetime import date

class TuteurForm(PersonneForm):
    class Meta(PersonneForm.Meta):
        model = Tuteur
        fields = PersonneForm.Meta.fields
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
            'lieu_naissance': forms.TextInput(attrs={'class': 'form-control'}),
            'sexe': forms.Select(attrs={'class': 'form-select'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'nationalite': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'situation_matrimoniale': forms.Select(attrs={'class': 'form-select'}),
            'profession': forms.TextInput(attrs={'class': 'form-control'}),
            'matricule': forms.TextInput(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'statut_user': forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_naissance = cleaned_data.get('date_naissance')
        today = date.today()
        # Validation date de naissance
        if date_naissance and date_naissance > today:
            self.add_error('date_naissance', "La date de naissance ne peut pas être dans le futur.")

        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.date_naissance:
           self.fields['date_naissance'].initial = self.instance.date_naissance.strftime('%Y-%m-%d')
        if self.instance and not self.instance.statut_user:
            self.instance.statut_user = "tuteur"
