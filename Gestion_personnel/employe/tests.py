from django.test import TestCase

# Create your tests here.
from datetime import date
from Gestion_personnel.employe.models import Employe


# Création de 15 employés
for i in range(1, 16):
    Employe.objects.create(
        username=f"user{i}",
        matricule=f"EMP{i:03}",  # EMP001, EMP002, ...
        first_name=f"Prenom{i}",
        last_name=f"Nom{i}",
        date_naissance=date(1990, 1, (i if i <= 28 else 28)),  # date de naissance valide
        lieu_naissance=f"Ville{i}",
        sexe='M' if i % 2 == 0 else 'F',
        telephone=f"69000000{i:02}",
        nationalite="CD",
        adresse=f"Adresse {i}",
        grade=f"Grade{i%5 + 1}",  # Grade1 à Grade5
        echelle=(i % 5) + 1,
        categorie=f"Cat{i%3 + 1}",  # Cat1 à Cat3
        statut_user="employé(e)"
    )
