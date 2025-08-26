from django import forms
from .models import Adherent
from referentiel.personne.forms import PersonneForm
from Gestion_adherent.Inscription_adherent.tuteur.models import Tuteur
from datetime import date

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
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'lieu_naissance': forms.TextInput(attrs={'class': 'form-control'}),  # <- ici
            'sexe': forms.Select(attrs={'class': 'form-select'}),  # <- et ici
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and not self.instance.statut_user:
            self.instance.statut_user = "adherent"

        today = date.today()
        self.fields['pere'].queryset = Tuteur.objects.filter(
            sexe='M', date_naissance__lte=date(today.year - 18, today.month, today.day)
        )
        self.fields['mere'].queryset = Tuteur.objects.filter(
            sexe='F', date_naissance__lte=date(today.year - 18, today.month, today.day)
        )
