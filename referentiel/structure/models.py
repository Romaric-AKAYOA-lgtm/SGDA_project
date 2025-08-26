from django.db import models

class Structure(models.Model):
    raison_sociale = models.CharField(max_length=150, unique=True)
    date_creation = models.DateTimeField()
    structure_sous_tutelle = models.CharField(max_length=512)
    adresse = models.CharField(max_length=512)
    email = models.EmailField(max_length=30, unique=True)
    pays_residence = models.CharField(max_length=20)
    devise_pays = models.CharField(max_length=30)
    direction_tutelle = models.CharField(max_length=30)
    telephone = models.CharField(max_length=15, unique=True)
    matricule = models.CharField(max_length=15, unique=True)
    logo_structure = models.ImageField(upload_to='logos/', null=True, blank=True)
    drapeau_pays = models.ImageField(upload_to='drapeaux/', null=True, blank=True)
    lieu_residence = models.CharField(max_length=20)

    def __str__(self):
        return self.raison_sociale
