from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from Gestion_personnel.operation.models import Operation
from django.utils import timezone


class AbsenceManager(models.Manager):
    def recentes(self):
        now = timezone.now()
        return self.get_queryset().filter(
            models.Q(date_retour_effective__isnull=True) | models.Q(date_retour_effective__gte=now)
        )


class Absence(models.Model):
    TYPE_ABSENCE_CHOICES = [
        ('conge_annuel', 'Congé Annuel'),
        ('absence_imprevue', 'Absence Imprévue'),
    ]

    STATUT_CHOICES = [
        ('annule', 'Annulé'),
        ('confirme', 'Confirmé'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
    ]

    date_creation = models.DateTimeField(auto_now_add=True)
    type_absence = models.CharField(max_length=20, choices=TYPE_ABSENCE_CHOICES)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES)
    date_debut = models.DateTimeField()
    duree = models.IntegerField(help_text="Durée de l'absence en jours")
    date_retour = models.DateTimeField(editable=False)  # ✅ Calculé automatiquement
    date_retour_effective = models.DateTimeField(null=True, blank=True)
    lieu = models.CharField(max_length=50)
    motif = models.CharField(max_length=255, null=True, blank=True)
    numero_note = models.IntegerField(null=True, blank=True)
    numero_fiche = models.IntegerField(null=True, blank=True)

    id_absence_operation_employe = models.ForeignKey(
        Operation,
        on_delete=models.CASCADE,
        related_name='absences_employe'
    )
    id_absence_operation_employe_respensable = models.ForeignKey(
        Operation,
        on_delete=models.CASCADE,
        related_name='absences_responsable'
    )
    id_absence_operation_employe_enregistre = models.ForeignKey(
        Operation,
        on_delete=models.CASCADE,
        related_name='absences_enregistreur'
    )

    def save(self, *args, **kwargs):
        """ ✅ Calcule automatiquement la date de retour """
        if self.date_debut and self.duree:
            self.date_retour = self.date_debut + timedelta(days=self.duree)
        else:
            self.date_retour = None
        super().save(*args, **kwargs)

    def clean(self):
        """ ✅ Valide certaines règles de gestion """
        # Évite les erreurs si les ForeignKey ne sont pas encore définies
        if not self.id_absence_operation_employe_id or \
           not self.id_absence_operation_employe_respensable_id or \
           not self.id_absence_operation_employe_enregistre_id:
            return

        # ✅ Vérifie que la date de retour effective ne peut pas être avant la date de début
        if self.date_retour_effective and self.date_retour_effective < self.date_debut:
            raise ValidationError(_("La date de retour effective doit être postérieure à la date de début."))

        # ✅ Contrôle spécifique pour congé annuel
        if self.type_absence == 'conge_annuel':
            if self.duree != 30:
                raise ValidationError(_("La durée du congé annuel doit être exactement de 30 jours."))

            expected_date_retour = self.date_debut + timedelta(days=30)
            if self.date_retour and self.date_retour != expected_date_retour:
                raise ValidationError(_("La date de retour doit être exactement 30 jours après la date de début."))

    def __str__(self):
        return f"Absence {self.id} - {self.get_type_absence_display()}"

    class Meta:
        verbose_name = "Absence"
        verbose_name_plural = "Absences"
