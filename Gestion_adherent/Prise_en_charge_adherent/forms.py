from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q
from Gestion_adherent.Inscription_adherent.adherent.models import Adherent
from Gestion_personnel.operation.models import Operation
from compte.views import get_employe_id_connecte
from .models import PriseEnChargeAdherent

class PriseEnChargeAdherentForm(forms.ModelForm):
    class Meta:
        operation_medecin= forms.ModelChoiceField(
            queryset=Operation.objects.none(),
            widget=forms.Select(attrs={'class': 'form-control select2'}),
            label="Médecin",
            required=True
        )
        adheren= forms.ModelChoiceField(
            queryset=Adherent.objects.none(),
            widget=forms.Select(attrs={'class': 'form-control select2'}),
            label="Adhérent",
            required=True
        )
        operation_enregistrer = forms.ModelChoiceField(
            queryset=Operation.objects.none(),
            widget=forms.Select(attrs={'class': 'form-control select2'}),
            label="Opération de l'utilisateur connecté",
            required=True
        )
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
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        today = timezone.now().date()

        # Opérations valides pour les employés
        med_mut = Operation.objects.filter(
            type_operation='mutation',
            statut='confirme',
        ).filter(
            Q(date_fin__isnull=True) | Q(date_fin__date__gte=today)
        ).order_by('-date_creation')
        if med_mut:
            self.fields['operation_medecin'].queryset = med_mut
            #self.fields['adherent'].initial = ad_act.pk

        ad_act = Adherent.objects.filter(statut=Adherent.STATUT_ACTIF)
        if ad_act:
            self.fields['adherent'].queryset = ad_act 
            #self.fields['adherent'].initial = ad_act.pk

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
                    self.fields['operation_enregistrer'].queryset = Operation.objects.filter(pk=op.pk)
                    self.fields['operation_enregistrer'].initial = op.pk

    def clean(self):
        cleaned_data = super().clean()
        operation_medecin = cleaned_data.get('operation_medecin')
        nom_complet_medecin = cleaned_data.get('nom_complet_medecin')
        fonction_medecin = cleaned_data.get('fonction_medecin')
        data = super().clean()

        # Vérifier qu'il existe une opération valide pour l'utilisateur connecté
        if not self._employe_connecte:
            raise ValidationError("Aucune opération valide trouvée pour l'utilisateur connecté.")

        # Forcer le champ operation
        data['operation_enregistrer'] = self._employe_connecte

        # Validation : si pas d'opération médecin, nom et fonction doivent être renseignés
        if not operation_medecin:
            if not nom_complet_medecin or not fonction_medecin:
                raise forms.ValidationError(
                    "Si l'opération médecin n'est pas renseignée, le nom complet et la fonction du médecin doivent être fournis."
                )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Assigner l'employé connecté comme opération
        if self._employe_connecte:
            instance.operation = self._employe_connecte
        if commit:
            instance.save()
        return instance