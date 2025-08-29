from datetime import timedelta
from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from .models import Operation, Employe
from compte.views import get_employe_id_connecte


class OperationForm(forms.ModelForm):
    id_employe = forms.ModelChoiceField(
        queryset=Employe.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select select2'}),
        label="Employé concerné",
        required=True
    )

    id_employe_responsable = forms.ModelChoiceField(
        queryset=Employe.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select select2'}),
        label="Employé responsable",
        required=False
    )

    id_employe_enregistre = forms.ModelChoiceField(
        queryset=Employe.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-select select2',
             'disabled': 'disabled'
        }),
        label="Employé enregistreur",
        required=False
    )

    class Meta:
        model = Operation
        exclude = []
        widgets = {
            'numero_note': forms.NumberInput(attrs={'class': 'form-control'}),
            'numero_fiche': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_debut': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'date_fin': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                #'readonly': True
            }),
            'type_operation': forms.Select(attrs={'class': 'form-select select2'}),
            'statut': forms.Select(attrs={'class': 'form-select select2'}),
            'id_organisation_unite': forms.Select(attrs={'class': 'form-select select2'}),
            'id_fonction': forms.Select(attrs={'class': 'form-select select2'}),
        }

        labels = {
            'numero_note': "Numéro de la note",
            'numero_fiche': "Numéro de la fiche",
            'date_debut': "Date de début",
            'date_fin': "Date de fin",
            'type_operation': "Type d'opération",
            'statut': "Statut de l'opération",
            'id_organisation_unite': "Service",
            'id_fonction': "Fonction",
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        today = timezone.now().date()

        # 1️⃣ Liste des employés actifs
        self.fields['id_employe'].queryset = Employe.objects.filter(statut='actif')

        # 2️⃣ Définir le responsable : dernière mutation confirmée
        resp = Operation.objects.filter(
            type_operation='mutation',
            statut='confirme',
            id_fonction__fonction_parent__isnull=True
        ).filter(
            Q(date_fin__isnull=True) | Q(date_fin__date__gte=today)
        ).order_by('-date_creation').first()

        if resp:
            self.fields['id_employe_responsable'].queryset = Employe.objects.filter(pk=resp.id_employe.pk)
            self.fields['id_employe_responsable'].initial = resp.id_employe.pk
        else:
            self.fields['id_employe_responsable'].queryset = Employe.objects.none()

        # 3️⃣ Employé enregistreur = utilisateur connecté
        self._employe_connecte = None
        if self.request and self.request.user.is_authenticated:
            emp_id = get_employe_id_connecte(self.request)
            if emp_id:
                self._employe_connecte = get_object_or_404(Employe, pk=emp_id)
                self.fields['id_employe_enregistre'].queryset = Employe.objects.filter(pk=self._employe_connecte.pk)
                self.fields['id_employe_enregistre'].initial = self._employe_connecte.pk

        # 4️⃣ Initialiser les champs de date lors de la modification
        if not self.data:
            for field_name in ['date_debut', 'date_fin']:
                value = getattr(self.instance, field_name, None)
                if value:
                    if timezone.is_aware(value):
                        value = timezone.localtime(value)
                    self.fields[field_name].initial = value.strftime('%Y-%m-%dT%H:%M')

    def clean(self):
        data = super().clean()

        # Vérifier la présence de l'utilisateur connecté
        if not self._employe_connecte:
            raise ValidationError("Impossible d'identifier l'employé enregistreur.")

        # Forcer la valeur pour l'employé enregistreur
        data['id_employe_enregistre'] = self._employe_connecte

        # Vérifier que la date de début n'est pas dans le passé
        date_debut = data.get('date_debut')
        if date_debut and date_debut.date() < timezone.now().date():
            self.add_error('date_debut', "La date de début ne peut pas être antérieure à aujourd'hui.")

        # ✅ Vérifier qu'une mutation est précédée d'une affectation confirmée
        type_operation = data.get('type_operation')
        employe = data.get('id_employe')

        if type_operation == 'mutation' and employe:
            affectation_existe = Operation.objects.filter(
                id_employe=employe,
                type_operation='affectation',
                statut='confirme'
            ).exists()

            if not affectation_existe:
                self.add_error(
                    'id_employe',
                    "Impossible d'effectuer une mutation : cet employé n'a pas encore d'affectation confirmée."
                )

        return data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.id_employe_enregistre = self._employe_connecte

        # ✅ Mettre à jour la date_fin de l'ancienne opération
        if instance.statut == 'confirme' and instance.type_operation in ['mutation', 'affectation']:
            ancienne_op = Operation.objects.filter(
                id_employe=instance.id_employe,
                type_operation=instance.type_operation,
                statut='confirme'
            ).exclude(pk=instance.pk).order_by('-date_debut').first()

            if ancienne_op:
                ancienne_op.date_fin = instance.date_debut - timedelta(days=1)
                ancienne_op.save()

        # ✅ Calculer la date de fin si elle n'est pas renseignée
        if not instance.date_fin and instance.date_debut:
            instance.date_fin = instance.date_debut + timedelta(days=1)

        if commit:
            instance.save()
        return instance
