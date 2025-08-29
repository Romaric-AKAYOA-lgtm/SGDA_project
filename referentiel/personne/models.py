from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from datetime import date

class Personne(AbstractUser):
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]

    STATUT_ACTIF = 'actif'
    STATUT_INACTIF = 'inactif'
    STATUT_CHOICES = [
        (STATUT_ACTIF, 'Actif'),
        (STATUT_INACTIF, 'Inactif'),
    ]

    SITUATION_CHOICES = [
        ('celibataire', 'Célibataire'),
        ('marie', 'Marié(e)'),
        ('divorce', 'Divorcé(e)'),
        ('veuf', 'Veuf/Veuve'),
        ('non_renseigne', 'Non renseigné'),
    ]
        
    # Informations personnelles
    matricule = models.CharField(max_length=7, unique=True, blank=True,null=True)
    date_naissance = models.DateField(null=True, blank=True)
    lieu_naissance = models.CharField(max_length=30, blank=True, null=True)
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES, blank=True, null=True)
    telephone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    nationalite = models.CharField(max_length=30, blank=True, null=True)
    situation_matrimoniale = models.CharField(
        max_length=20,
        choices=SITUATION_CHOICES,
        default='non_renseigne',
        blank=True,
        null=True
    )
    profession = models.CharField(max_length=50, blank=True, null=True)
    adresse = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='profiles/', null=True, blank=True)

    # Statuts
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default=STATUT_ACTIF)
    statut_user = models.CharField(max_length=10, blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username or 'Sans identifiant'} ({self.matricule})"

    def clean(self):
        """Valide les champs personnalisés avant la sauvegarde"""
        if self.date_naissance:
            if self.date_naissance > date.today():
                raise ValidationError("La date de naissance ne peut pas être dans le futur.")

            age = self.calculate_age(self.date_naissance)
            if age < 0:
                raise ValidationError("La personne doit avoir au moins 18 ans.")

        super().clean()

    @staticmethod
    def calculate_age(date_naissance):
        """Calcule l’âge"""
        today = date.today()
        return today.year - date_naissance.year - (
            (today.month, today.day) < (date_naissance.month, date_naissance.day)
        )
