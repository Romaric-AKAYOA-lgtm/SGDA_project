from django.db import models
from django.utils import timezone

from Gestion_adherent.Inscription_adherent.adherent.models import Adherent
from Gestion_personnel.operation.models import Operation

class Cotisation(models.Model):
    # Constantes pour le statut
    STATUT_VALIDE = 'valide'
    STATUT_INVALIDE = 'invalide'

    STATUT_CHOICES = [
        (STATUT_VALIDE, 'Valide'),
        (STATUT_INVALIDE, 'Invalide'),
    ]

    TYPE_COTISATION_CHOICES = [
        ('mensuelle', 'Mensuelle'),
        ('annuelle', 'Annuelle'),
        ('ponctuelle', 'Ponctuelle'),
        # ajouter d'autres types si nécessaire
    ]

    adherent = models.ForeignKey(Adherent, on_delete=models.CASCADE, related_name='cotisations')
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE, related_name='cotisations')
    date_cotisation = models.DateField(default=timezone.now)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default=STATUT_VALIDE)
    type_cotisation = models.CharField(max_length=20, choices=TYPE_COTISATION_CHOICES)

    class Meta:
        verbose_name = "Cotisation"
        verbose_name_plural = "Cotisations"
        ordering = ['-date_cotisation']

    def save(self, *args, **kwargs):
        """
        Met à jour le statut automatiquement.
        Si le type de cotisation est valide (logique métier à définir), le statut = valide.
        Sinon, il peut être invalide.
        """
        # Exemple simplifié : ici tu peux ajouter la logique réelle de validation selon ton type_cotisation
        if self.type_cotisation and self.montant > 0:
            self.statut = self.STATUT_VALIDE
        else:
            self.statut = self.STATUT_INVALIDE

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.adherent} - {self.type_cotisation} ({self.statut})"
