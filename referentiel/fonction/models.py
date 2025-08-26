from django.db import models
from referentiel.structure.models import Structure

class Fonction(models.Model):
    designation = models.CharField(max_length=50, unique=True)
    fonction_parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sous_fonctions'
    )
    structure = models.ForeignKey(
        Structure,
        on_delete=models.CASCADE,
        related_name='fonctions'
    )

    def __str__(self):
        return self.designation
