from django.db import models
from django.core.exceptions import ValidationError
from Gestion_adherent.Inscription_adherent.tuteur.models import Tuteur
from referentiel.personne.models import Personne
from datetime import date

class Adherent(Personne):
    pere = models.ForeignKey(
        Tuteur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enfants_pere',
        limit_choices_to={'sexe': 'M'},  # sexe masculin
    )
    mere = models.ForeignKey(
        Tuteur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enfants_mere',
        limit_choices_to={'sexe': 'F'},  # sexe féminin
    )

    def clean(self):
        """Validation des tuteurs lors de l'enregistrement."""
        # Vérifier l'âge minimum de 18 ans pour le père
        if self.pere:
            today = date.today()
            age_pere = (today - self.pere.date_naissance).days // 365
            if age_pere < 18:
                raise ValidationError({'pere': "Le père doit avoir au moins 18 ans."})
        
        # Vérifier l'âge minimum de 18 ans pour la mère
        if self.mere:
            today = date.today()
            age_mere = (today - self.mere.date_naissance).days // 365
            if age_mere < 18:
                raise ValidationError({'mere': "La mère doit avoir au moins 18 ans."})

    def save(self, *args, **kwargs):
        if not self.statut_user:
            self.statut_user = "adherent"
        # Exécuter la validation custom avant save
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Adhérent"
        verbose_name_plural = "Adhérents"
