from django.db import models
from referentiel.personne.models import Personne  # adapte selon ton organisation

class Employe(Personne):
    grade = models.CharField(max_length=20)
    echelle = models.IntegerField()
    categorie = models.CharField(max_length=10)

    def save(self, *args, **kwargs):
        if not self.statut_user:
            self.statut_user = "employé(e)"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.telephone}"

    @classmethod
    def get_employes_actifs(cls):
        """
        Retourne une liste de tuples (first_name, last_name, matricule)
        des employés ayant le statut 'actif'.
        """
        return cls.objects.filter(statut="actif").values_list('first_name', 'last_name', 'matricule')
