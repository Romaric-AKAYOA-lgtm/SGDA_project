from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from referentiel.fonction.models import Fonction
from referentiel.organisation_unite.models import OrganisationUnite
from Gestion_personnel.employe.models import Employe


class OperationManager(models.Manager):
    def recentes(self):
        today = timezone.now()
        return self.filter(models.Q(date_fin__isnull=True) | models.Q(date_fin__gte=today))


class Operation(models.Model):
    STATUT_CHOICES = [
        ('confirme', 'Confirmé'),
        ('annule', 'Annulé'),
    ]

    TYPE_CHOICES = [
        ('affectation', 'Affectation'),
        ('mutation', 'Mutation'),
    ]

    date_creation = models.DateTimeField(auto_now_add=True)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField(null=True, blank=True)

    statut = models.CharField(max_length=10, choices=STATUT_CHOICES)
    numero_note = models.PositiveIntegerField(unique=True)
    numero_fiche = models.PositiveIntegerField(unique=True)
    type_operation = models.CharField(max_length=12, choices=TYPE_CHOICES)

    id_employe = models.ForeignKey(
        Employe,
        on_delete=models.CASCADE,
        related_name='operations_employe'
    )
    id_organisation_unite = models.ForeignKey(
        OrganisationUnite,
        on_delete=models.CASCADE
    )
    id_fonction = models.ForeignKey(
        Fonction,
        on_delete=models.CASCADE
    )
    id_employe_responsable = models.ForeignKey(
        Employe,
        on_delete=models.CASCADE,
        related_name='operations_responsable'
    )
    id_employe_enregistre = models.ForeignKey(
        Employe,
        on_delete=models.CASCADE,
        related_name='operations_enregistreur'
    )

    objects = OperationManager()

    def clean(self):
        # Vérifier que la date de début est cohérente
        if self.date_fin and self.date_debut > self.date_fin:
            raise ValidationError("La date de fin ne peut pas être antérieure à la date de début.")

        # Si le statut est "annulé", on force la date de fin à la date actuelle
        if self.statut == 'annule' and not self.date_fin:
            self.date_fin = timezone.now()

    def save(self, *args, **kwargs):
        self.full_clean()  # Exécute la validation avant l'enregistrement
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id_employe.last_name} {self.id_employe.first_name} - {self.id_fonction.designation}"

    class Meta:
        verbose_name = "Opération"
        verbose_name_plural = "Opérations"
        ordering = ["-date_creation"]
