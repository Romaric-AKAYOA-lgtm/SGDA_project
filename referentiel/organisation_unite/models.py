from django.db import models
from referentiel.unite.models import Unite
from referentiel.structure.models import Structure

class OrganisationUnite(models.Model):
    designation = models.CharField(max_length=30, unique=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    organisation_unite_parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sous_organisations'
    )
    
    unite = models.ForeignKey(
        Unite,
        on_delete=models.CASCADE,
        related_name='organisations'
    )

    structure = models.ForeignKey(
        Structure,
        on_delete=models.CASCADE,
        related_name='organisations_unites'
    )

    def __str__(self):
        return self.designation
