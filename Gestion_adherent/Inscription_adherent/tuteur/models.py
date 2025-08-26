
from referentiel.personne.models import Personne  # adapte selon ton organisation

class Tuteur(Personne):

    def save(self, *args, **kwargs):
        if not self.statut_user:
            self.statut_user = "tuteur"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Tuteur"
        verbose_name_plural = "Tuteurs"
