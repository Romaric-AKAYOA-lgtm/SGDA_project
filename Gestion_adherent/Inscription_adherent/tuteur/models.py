
from datetime import date
from django.forms import ValidationError
from referentiel.personne.models import Personne  # adapte selon ton organisation

from referentiel.personne.models import Personne  # adapte selon ton organisation
class Tuteur(Personne):
    def clean(self):
        # Exemples de validations
        if self.date_naissance and self.date_naissance > date.today():
            raise ValidationError({'date_naissance': "La date de naissance ne peut pas être dans le futur."})
        if not self.telephone and not self.email:
            raise ValidationError("Au moins un contact (téléphone ou email) doit être renseigné.")

    def save(self, *args, **kwargs):
        self.full_clean()  # appelle clean() avant de sauvegarder
        if not self.statut_user:
            self.statut_user = "tuteur"
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
