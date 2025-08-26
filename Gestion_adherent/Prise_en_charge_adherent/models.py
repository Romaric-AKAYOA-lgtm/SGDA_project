from django.db import models
from django.utils import timezone

from Gestion_adherent.Inscription_adherent.adherent.models import Adherent
from Gestion_personnel.operation.models import Operation

class PriseEnChargeAdherent(models.Model):
    objet = models.CharField(max_length=255)
    description = models.TextField()
    date_creation = models.DateTimeField(default=timezone.now)

    # Informations du médecin
    nom_complet_medecin = models.CharField(max_length=255, blank=True, null=True)
    fonction_medecin = models.CharField(max_length=100, blank=True, null=True)
    specialite_medecin = models.CharField(max_length=100, blank=True, null=True)

    # Clés étrangères
    adherent = models.ForeignKey(Adherent, on_delete=models.CASCADE, related_name='prises_en_charge')
    operation_enregistrer = models.ForeignKey(Operation, on_delete=models.CASCADE, related_name='prises_en_charge_enregistrees')
    operation_medecin = models.ForeignKey(Operation, on_delete=models.SET_NULL, related_name='prises_en_charge_medecins', blank=True, null=True)

    class Meta:
        verbose_name = "Prise en charge Adhérent"
        verbose_name_plural = "Prises en charge Adhérents"
        ordering = ['-date_creation']

    def save(self, *args, **kwargs):
        # Si operation_medecin n'est pas renseignée, nom_complet_medecin et fonction_medecin doivent l'être
        if not self.operation_medecin:
            if not self.nom_complet_medecin or not self.fonction_medecin:
                raise ValueError(
                    "Si l'opération médecin n'est pas renseignée, le nom complet et la fonction du médecin doivent être fournis."
                )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.objet} - {self.nom_complet_medecin or 'Médecin via opération'} ({self.date_creation.strftime('%d/%m/%Y')})"
