from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from Gestion_adherent.Inscription_adherent.adherent.models import Adherent
from Gestion_adherent.Inscription_adherent.tuteur.models import Tuteur

class SuiviTuteurAdherent(models.Model):
    STATUT_CHOICES = [
        ('pere', 'Père'),
        ('mere', 'Mère'),
        ('autre', 'Autre'),
    ]

    adherent = models.ForeignKey(
        Adherent, on_delete=models.CASCADE, related_name='tuteurs'
    )
    tuteur = models.ForeignKey(
        Tuteur, on_delete=models.CASCADE, related_name='adherents'
    )
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES)
    date_creation = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Suivi Tuteur-Adhérent"
        verbose_name_plural = "Suivis Tuteur-Adhérent"
        unique_together = ('adherent', 'tuteur')  # empêcher doublons

    def clean(self):
        """
        Validation avant sauvegarde :
        - Le tout premier tuteur doit être soit le père ou la mère.
        """
        if not self.pk:  # uniquement à la création
            existing_tuteurs = SuiviTuteurAdherent.objects.filter(adherent=self.adherent)
            if not existing_tuteurs.exists() and self.statut not in ['pere', 'mere']:
                raise ValidationError(
                    "Le tout premier tuteur doit être soit le père ou la mère de l'adhérent."
                )

    def save(self, *args, **kwargs):
        self.full_clean()  # appelle clean() avant de sauvegarder
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.adherent} - {self.tuteur} ({self.statut})"
