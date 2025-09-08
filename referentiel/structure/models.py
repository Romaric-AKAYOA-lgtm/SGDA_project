from django.db import models

class Structure(models.Model):
    # Informations générales
    raison_sociale = models.CharField(max_length=150, unique=True)
    date_creation = models.DateTimeField()
    structure_sous_tutelle = models.CharField(max_length=512, blank=True, null=True)
    adresse = models.CharField(max_length=512)
    email = models.EmailField(max_length=50, unique=True)
    telephone = models.CharField(max_length=20, unique=True)
    matricule = models.CharField(max_length=20, unique=True)
    lieu_residence = models.CharField(max_length=50)
    pays_residence = models.CharField(max_length=50)
    devise_pays = models.CharField(max_length=30, blank=True, null=True)
    direction_tutelle = models.CharField(max_length=50, blank=True, null=True)

    # Images
    logo_structure = models.ImageField(upload_to='logos/', null=True, blank=True)
    drapeau_pays = models.ImageField(upload_to='drapeaux/', null=True, blank=True)

    # Informations supplémentaires pour ONG
    numero_enregistrement = models.CharField(max_length=50, blank=True, null=True)
    forme_juridique = models.CharField(max_length=50, blank=True, null=True)
    site_web = models.URLField(blank=True, null=True)
    contact_personne = models.CharField(max_length=100, blank=True, null=True)
    domaines_activite = models.TextField(blank=True, null=True)
    zones_intervention = models.TextField(blank=True, null=True)
    statut = models.CharField(max_length=20, default='Actif')
    date_maj = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.raison_sociale
