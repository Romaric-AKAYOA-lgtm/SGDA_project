import uuid
from django.db import models
from django.utils.timezone import now, timedelta

class Activation(models.Model):
    key = models.CharField(max_length=100, unique=True, blank=True)
    activated_on = models.DateTimeField(auto_now_add=True)
    expires_on = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.key:
            # Générer la clé UUID
            uuid_part = str(uuid.uuid4())
            # Définir la date d'expiration à 30 jours à partir de maintenant
            expiration_date = now() + timedelta(days=30)
            # Formater la date d'expiration
            expiration_part = expiration_date.strftime("%Y%m%d%H%M")
            # Combiner UUID et date d'expiration dans une seule clé
            self.key = f"{uuid_part}-{expiration_part}"
            self.expires_on = expiration_date  # Assurez-vous de définir l'expiration également
        super().save(*args, **kwargs)

    def is_valid(self):
        """Retourne True si la clé est encore valide, False sinon."""
        return now() < self.expires_on

    def __str__(self):
        return f"Activation {self.key} (Expire le {self.expires_on.strftime('%Y-%m-%d %H:%M:%S')})"
