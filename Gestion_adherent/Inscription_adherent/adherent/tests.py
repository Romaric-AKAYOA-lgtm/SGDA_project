import os
import django
from datetime import date, timedelta

# ⚠️ Adapter au chemin de ton projet
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Gestion_Personnel_Visites_INRAP.settings")
django.setup()

from Gestion_adherent.Inscription_adherent.adherent.models import Adherent
from Gestion_adherent.Inscription_adherent.tuteur.models import Tuteur

# Supprimer tous les adhérents existants (optionnel)
Adherent.objects.all().delete()

# Récupérer quelques tuteurs existants pour les assigner aux adhérents
tuteurs_hommes = list(Tuteur.objects.filter(sexe='M'))
tuteurs_femmes = list(Tuteur.objects.filter(sexe='F'))
for i in range(1, 1001):  # exemple avec 100 adhérents
    pere = tuteurs_hommes[i % len(tuteurs_hommes)] if tuteurs_hommes else None
    mere = tuteurs_femmes[i % len(tuteurs_femmes)] if tuteurs_femmes else None

    adherent = Adherent(
        username=f"adherent{i:03}",
        matricule=f"ADH{i:04}",
        first_name=f"Prenom{i:03}",
        last_name=f"Nom{i:03}",
        date_naissance=date(1990, 1, 1) + timedelta(days=i*30 % 7300),
        lieu_naissance=f"Ville{i:03}",
        sexe='M' if i % 2 == 0 else 'F',
        email=f"adherent{i:03}@exemple.com",  # obligatoire
        nationalite="CD",
        adresse=f"Adresse {i:03}",
        situation_matrimoniale='non_renseigne',
        profession=f"Profession{i:03}",
        pere=pere,
        mere=mere,
        statut_user="adherent"
    )
    adherent.set_password("Adherent123!")  # mot de passe fictif
    adherent.save()


print("✅ 100 adhérents créés avec succès !")
