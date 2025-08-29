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
        """Validation des tuteurs et cohérence des données."""
        today = date.today()

        # Vérifier l'âge minimum de 18 ans pour le père
        if self.pere and self.pere.date_naissance:
            age_pere = today.year - self.pere.date_naissance.year - (
                (today.month, today.day) < (self.pere.date_naissance.month, self.pere.date_naissance.day)
            )
            if age_pere < 18:
                raise ValidationError({'pere': "Le père doit avoir au moins 18 ans."})

        # Vérifier l'âge minimum de 18 ans pour la mère
        if self.mere and self.mere.date_naissance:
            age_mere = today.year - self.mere.date_naissance.year - (
                (today.month, today.day) < (self.mere.date_naissance.month, self.mere.date_naissance.day)
            )
            if age_mere < 18:
                raise ValidationError({'mere': "La mère doit avoir au moins 18 ans."})

        # Vérifier que le père et la mère ne sont pas la même personne
        if self.pere and self.mere and self.pere == self.mere:
            raise ValidationError({'mere': "Le père et la mère ne peuvent pas être la même personne."})

        # Vérifier que la date de naissance de l'adhérent n'est pas dans le futur
        if self.date_naissance and self.date_naissance > today:
            raise ValidationError({'date_naissance': "La date de naissance ne peut pas être dans le futur."})

    def save(self, *args, **kwargs):
        # Définir le statut_user par défaut si vide
        if not self.statut_user:
            self.statut_user = "adherent"
        # Valider les données avant sauvegarde
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Adhérent"
        verbose_name_plural = "Adhérents"
