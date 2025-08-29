from datetime import date, datetime
from django import forms
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils import timezone

from Gestion_adherent.Inscription_adherent.adherent.models import Adherent
from compte.views import get_employe_id_connecte
from .models import Cotisation, Operation

class CotisationForm(forms.ModelForm):
    adherent = forms.ModelChoiceField(
            queryset=Adherent.objects.none(),
            widget=forms.Select(attrs={'class': 'form-control select2'}),
            label='Adhérent',
            required=True
        )
    operation = forms.ModelChoiceField(
        queryset=Operation.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control select2'}),
        label="Opération de l'utilisateur connecté",
        required=True
    )

    class Meta:
        model = Cotisation
        fields = [
            'adherent',
            'operation',
            'montant',
            'type_cotisation',
            'statut',
        ]
        widgets = {
            'adherent': forms.Select(attrs={'class': 'form-select select2', 'placeholder': 'Sélectionner un adhérent'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'type_cotisation': forms.Select(attrs={'class': 'form-select'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'adherent': 'Adhérent',
            'montant': 'Montant de la prise en charge',
            'type_cotisation': 'Type de cotisation',
            'statut': 'Statut',
        }
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        today = timezone.now().date()
        ad_act = Adherent.objects.filter(statut=Adherent.STATUT_ACTIF)
        if ad_act:
            self.fields['adherent'].queryset = ad_act 
        # Récupération de l'opération de l'utilisateur connecté
        self._employe_connecte = None
        if self.request and self.request.user.is_authenticated:
            emp_id = get_employe_id_connecte(self.request)
            if emp_id:
                op = Operation.objects.filter(
                    id_employe=emp_id,
                    type_operation='mutation',
                    statut='confirme'
                ).filter(
                    Q(date_fin__isnull=True) | Q(date_fin__date__gte=today)
                ).order_by('-date_debut').first()

                if op:
                    self._employe_connecte = op
                    self.fields['operation'].queryset = Operation.objects.filter(pk=op.pk)
                    self.fields['operation'].initial = op.pk


    def clean_montant(self):
        montant = self.cleaned_data.get('montant')
        if montant is None or montant <= 0:
            raise forms.ValidationError("Le montant doit être supérieur à 0.")
        return montant

    def clean(self):
        data = super().clean()

        # Vérifier qu'il existe une opération valide pour l'utilisateur connecté
        if not self._employe_connecte:
            raise ValidationError("Aucune opération valide trouvée pour l'utilisateur connecté.")

        # Forcer le champ operation
        data['operation'] = self._employe_connecte

        # Ajuster le statut si type_cotisation renseigné
        type_cotisation = data.get('type_cotisation')
        statut = data.get('statut')
        if type_cotisation and statut != 'valide':
            data['statut'] = 'valide'

        return data

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Assigner l'employé connecté comme opération
        if self._employe_connecte:
            instance.operation = self._employe_connecte
        if commit:
            instance.save()
        return instance
