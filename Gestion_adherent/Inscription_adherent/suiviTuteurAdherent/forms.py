from django import forms

from Gestion_adherent.Inscription_adherent.adherent.models import Adherent
from Gestion_adherent.Inscription_adherent.tuteur.models import Tuteur
from .models import SuiviTuteurAdherent
from django.utils import timezone

class SuiviTuteurAdherentForm(forms.ModelForm):
    adherent = forms.ModelChoiceField(
            queryset=Adherent.objects.none(),
            widget=forms.Select(attrs={'class': 'form-control select2'}),
            label='Adhérent',
            required=True
        )
    tuteur = forms.ModelChoiceField(
        queryset=Tuteur.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control select2'}),
        label="Tuteur",
        required=True
    )
    class Meta:
        model = SuiviTuteurAdherent
        fields = ['adherent', 'tuteur', 'statut']
        widgets = {
            'adherent': forms.Select(attrs={'class': 'form-select select2'}),
            'tuteur': forms.Select(attrs={'class': 'form-select select2'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        ad_act = Adherent.objects.filter(statut=Adherent.STATUT_ACTIF)
        if ad_act:
            self.fields['adherent'].queryset = ad_act 
        tuteur_act=Tuteur.objects.filter(statut=Tuteur.STATUT_ACTIF)
        if ad_act:
            self.fields['tuteur'].queryset = tuteur_act

    def clean_statut(self):
        statut = self.cleaned_data.get('statut')
        adherent = self.cleaned_data.get('adherent')
        tuteur = self.cleaned_data.get('tuteur')

        if not adherent or not tuteur:
            return statut  # la validation sera faite plus tard

        # Vérifier si c'est le premier tuteur
        if not SuiviTuteurAdherent.objects.filter(adherent=adherent).exists():
            if statut not in ['pere', 'mere']:
                raise forms.ValidationError(
                    "Le tout premier tuteur doit être soit le père ou la mère de l'adhérent."
                )

        # Vérifier âge du tuteur minimum 18 ans
        from datetime import date
        if tuteur.date_naissance:
            age = (date.today() - tuteur.date_naissance).days // 365
            if age < 18:
                raise forms.ValidationError("Le tuteur doit avoir au moins 18 ans.")

        # Vérifier sexe du tuteur si statut père/mère
        if statut == 'pere' and tuteur.sexe != 'M':
            raise forms.ValidationError("Le tuteur désigné comme père doit être de sexe masculin.")
        if statut == 'mere' and tuteur.sexe != 'F':
            raise forms.ValidationError("Le tuteur désigné comme mère doit être de sexe féminin.")

        return statut
