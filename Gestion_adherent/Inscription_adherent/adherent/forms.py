from django import forms
from .models import Adherent
from referentiel.personne.forms import PersonneForm
from Gestion_adherent.Inscription_adherent.tuteur.models import Tuteur
from datetime import date
from django.core.exceptions import ValidationError

class AdherentForm(PersonneForm):
    pere = forms.ModelChoiceField(
        queryset=Tuteur.objects.none(),
        required=False,
        label="Père",
        help_text="Le père doit avoir au moins 18 ans",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    mere = forms.ModelChoiceField(
        queryset=Tuteur.objects.none(),
        required=False,
        label="Mère",
        help_text="La mère doit avoir au moins 18 ans",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta(PersonneForm.Meta):
        model = Adherent
        fields = PersonneForm.Meta.fields + ['pere', 'mere']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'lieu_naissance': forms.TextInput(attrs={'class': 'form-control'}),
            'sexe': forms.Select(attrs={'class': 'form-select'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'matricule': forms.TextInput(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialiser le statut_user pour l'adhérent
        if self.instance and not self.instance.statut_user:
            self.instance.statut_user = "adherent"

        # Filtrer les tuteurs éligibles : au moins 18 ans
        today = date.today()
        age_limit = today.replace(year=today.year - 18)
        self.fields['pere'].queryset = Tuteur.objects.filter(statut=Tuteur.STATUT_ACTIF, sexe='M', date_naissance__lte=age_limit)
        self.fields['mere'].queryset = Tuteur.objects.filter(statut=Tuteur.STATUT_ACTIF, sexe='F', date_naissance__lte=age_limit)

    def clean(self):
        cleaned_data = super().clean()
        date_naissance = cleaned_data.get('date_naissance')
        pere = cleaned_data.get('pere')
        mere = cleaned_data.get('mere')
        today = date.today()
        age_limit = today.replace(year=today.year - 18)

        # Validation date de naissance
        if date_naissance and date_naissance > today:
            self.add_error('date_naissance', "La date de naissance ne peut pas être dans le futur.")

        # Validation âge des tuteurs si renseignés
        if pere and pere.date_naissance > age_limit:
            self.add_error('pere', "Le père doit avoir au moins 18 ans.")
        if mere and mere.date_naissance > age_limit:
            self.add_error('mere', "La mère doit avoir au moins 18 ans.")

        # Vérifier que le père et la mère ne sont pas les mêmes
        if pere and mere and pere == mere:
            self.add_error('mere', "Le père et la mère ne peuvent pas être la même personne.")

        return cleaned_data
