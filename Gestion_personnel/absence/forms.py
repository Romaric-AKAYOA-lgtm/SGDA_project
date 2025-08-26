from datetime import timedelta
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q

from Gestion_personnel.operation.models import Operation
from .models import Absence
from compte.views import get_employe_id_connecte

class AbsenceForm(forms.ModelForm):
    id_absence_operation_employe = forms.ModelChoiceField(
        queryset=Operation.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select select2'}),
        label="Employé concerné",
        required=True
    )

    id_absence_operation_employe_respensable = forms.ModelChoiceField(
        queryset=Operation.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select select2'}),
        label="Responsable",
        required=True
    )

    id_absence_operation_employe_enregistre = forms.ModelChoiceField(
        queryset=Operation.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control select2'}),
        label="Employé enregistreur",
        required=True
    )

    class Meta:
        model = Absence
        fields = '__all__'
        widgets = {
            'date_debut': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'  # <-- Format compatible datetime-local
            ),
            'date_retour': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control', 'readonly': 'readonly'},
                format='%Y-%m-%dT%H:%M'
            ),
            'date_retour_effective': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            ),
            'type_absence': forms.Select(attrs={'class': 'form-select'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'lieu': forms.TextInput(attrs={'class': 'form-control'}),
            'motif': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'duree': forms.NumberInput(attrs={'class': 'form-control'}),
            'numero_note': forms.NumberInput(attrs={'class': 'form-control'}),
            'numero_fiche': forms.NumberInput(attrs={'class': 'form-control'}),
        }

        labels = {
            'numero_note': "N° Note",
            'numero_fiche': "N° Fiche",
            'type_absence': "Type d'absence",
            'statut': "Statut de l'absence",
            'date_debut': "Date de début",
            'duree': "Durée (jours)",
            'date_retour': "Date de retour prévue",
            'date_retour_effective': "Date de retour effective",
            'lieu': "Lieu",
            'motif': "Motif",
            'id_absence_operation_employe': "Employé concerné",
            'id_absence_operation_employe_respensable': "Responsable",
            'id_absence_operation_employe_enregistre': "Enregistré par",
        }


    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        today = timezone.now().date()

        # Opérations valides pour les employés
        qs = Operation.objects.filter(
            type_operation='mutation'
        ).filter(
            Q(date_fin__isnull=True) | Q(date_fin__date__gte=today)
        )

        # Responsables = directeurs uniquement
        filtre_operations_directeur = Operation.objects.filter(
            type_operation='mutation',
            statut='confirme',
            id_fonction__fonction_parent__isnull=True
        ).filter(
            Q(date_fin__isnull=True) | Q(date_fin__date__gte=today)
        ).order_by('-date_creation')

        self.fields['id_absence_operation_employe'].queryset = qs
        self.fields['id_absence_operation_employe_respensable'].queryset = filtre_operations_directeur

        # Gestion de l'employé connecté
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
                    self.fields['id_absence_operation_employe_enregistre'].queryset = Operation.objects.filter(pk=op.pk)
                    self.fields['id_absence_operation_employe_enregistre'].initial = op.pk

        # Initialisation des champs date pour la modification
        if self.instance and self.instance.pk:
            for field_name in ['date_debut', 'date_retour', 'date_retour_effective']:
                if field_name in self.fields:
                    value = getattr(self.instance, field_name)
                    if value:
                        # Conversion en string compatible datetime-local
                        if timezone.is_aware(value):
                            value = timezone.localtime(value)
                        self.fields[field_name].initial = value.strftime('%Y-%m-%dT%H:%M')

    def clean(self):
        data = super().clean()

        # Vérifier qu'on a bien trouvé l'opération de l'employé connecté
        if not self._employe_connecte:
            raise ValidationError("Aucune opération valide trouvée pour l'utilisateur connecté.")

        # Forcer la valeur de l'employé enregistreur
        data['id_absence_operation_employe_enregistre'] = self._employe_connecte

        # Calcul automatique de la date de retour
        date_debut = data.get('date_debut')
        duree = data.get('duree')
        if date_debut and duree:
            data['date_retour'] = date_debut + timedelta(days=duree)

        # Vérification du type d'absence
        type_absence = data.get('type_absence')
        motif = data.get('motif')

        if type_absence == 'conge_annuel':
            if duree and duree != 30:
                self.add_error('duree', "La durée du congé annuel doit être exactement 30 jours.")
            if motif:
                self.add_error('motif', "Le champ 'Motif' ne doit pas être renseigné pour un congé annuel.")

        elif type_absence == 'absence_imprevue' and not motif:
            self.add_error('motif', "Le motif est obligatoire pour une absence imprévue.")

        return data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Calcul automatique de la date de retour
        if instance.date_debut and instance.duree:
            instance.date_retour = instance.date_debut + timedelta(days=instance.duree)

        # Assigner l'employé connecté comme enregistreur
        if self._employe_connecte:
            instance.id_absence_operation_employe_enregistre = self._employe_connecte

        if commit:
            instance.save()

        return instance
