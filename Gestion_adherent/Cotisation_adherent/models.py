from django.db import models
from django.utils import timezone
from Gestion_adherent.Inscription_adherent.adherent.models import Adherent
from Gestion_personnel.operation.models import Operation

class Cotisation(models.Model):
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
    ]

    adherent = models.ForeignKey(Adherent, on_delete=models.CASCADE, related_name='cotisations')
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE, related_name='cotisations')
    date_cotisation = models.DateTimeField(auto_now_add=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default=STATUT_INVALIDE)
    type_cotisation = models.CharField(max_length=20, choices=TYPE_COTISATION_CHOICES)

    class Meta:
        verbose_name = "Cotisation"
        verbose_name_plural = "Cotisations"
        ordering = ['-date_cotisation']

    def save(self, *args, **kwargs):
        now = timezone.now()

        if self.type_cotisation == 'annuelle':
            self.statut = self.STATUT_VALIDE if self.montant >= 100 and now.year == now.year else self.STATUT_INVALIDE
        elif self.type_cotisation == 'mensuelle':
            self.statut = self.STATUT_VALIDE if self.montant >= 10 and now.month == now.month else self.STATUT_INVALIDE
        elif self.type_cotisation == 'ponctuelle':
            self.statut = self.STATUT_VALIDE if self.montant > 0 and now.day == now.day else self.STATUT_INVALIDE
        else:
            self.statut = self.STATUT_INVALIDE

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.adherent} - {self.type_cotisation} ({self.statut})"
