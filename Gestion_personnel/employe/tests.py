import os
import django
from datetime import date

# ⚠️ Adapter à ton projet
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Gestion_Personnel_Visites_INRAP.settings")
django.setup()

from Gestion_personnel.employe.models import Employe

# Supprimer tous les employés existants
Employe.objects.all().delete()

# Création de 1984 employés
for i in range(1, 2000):
    tel = f"690000{i:04}"  # 6900000016, 6900000017, ... unique
    Employe.objects.create(
        username=f"user{i:04}",
        matricule=f"EMP{i:04}",
        first_name=f"Prenom{i}",
        last_name=f"Nom{i}",
        date_naissance=date(1990, 1, i if i <= 28 else 28),
        lieu_naissance=f"Ville{i}",
        sexe='M' if i % 2 == 0 else 'F',
        telephone=tel,
        nationalite="CD",
        adresse=f"Adresse {i}",
        grade=f"Grade{i%5 + 1}",
        echelle=(i % 5) + 1,
        categorie=f"Cat{i%3 + 1}",
        statut_user="employé(e)"
    )

print("✅ 1984 employés créés avec succès !")
