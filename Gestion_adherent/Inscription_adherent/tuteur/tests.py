import os
import django
from datetime import date, timedelta
import random

# ⚠️ Adapter au chemin de ton projet
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Gestion_Personnel_Visites_INRAP.settings")
django.setup()

from Gestion_adherent.Inscription_adherent.tuteur.models import Tuteur

# Supprimer tous les tuteurs existants (optionnel)
Tuteur.objects.all().delete()

# Création de 50 tuteurs fictifs
for i in range(1, 10001):
    sexe = 'M' if i % 2 == 0 else 'F'
    naissance = date.today() - timedelta(days=365*(25 + i % 36))

    tuteur = Tuteur(
        username=f"tuteur{i:03}",
        matricule=f"TUT{i:04}",
        first_name=f"Prenom{i:03}",
        last_name=f"Nom{i:03}",
        date_naissance=naissance,
        lieu_naissance=f"Ville{i:03}",
        sexe=sexe,
        telephone=f"690000{i:03}",
        email=f"tuteur{i:03}@exemple.com",  # obligatoire pour NOT NULL
        nationalite="CD",
        adresse=f"Adresse {i:03}",
        situation_matrimoniale='non_renseigne',
        profession=f"Profession{i:03}",
        statut_user="tuteur"
    )
    tuteur.set_password("Tuteur123!")
    tuteur.save()
