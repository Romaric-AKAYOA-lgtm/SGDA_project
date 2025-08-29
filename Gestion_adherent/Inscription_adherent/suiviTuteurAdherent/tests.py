import os
import django
from random import choice
from datetime import date

from Gestion_adherent.Inscription_adherent.suiviTuteurAdherent.models import SuiviTuteurAdherent

# ⚠️ Adapter au chemin de ton projet
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Gestion_Personnel_Visites_INRAP.settings")
django.setup()

from Gestion_adherent.Inscription_adherent.adherent.models import Adherent
from Gestion_adherent.Inscription_adherent.tuteur.models import Tuteur

# Supprimer les suivis existants (optionnel)
SuiviTuteurAdherent.objects.all().delete()

# Récupérer tous les adhérents et tuteurs existants
adherents = list(Adherent.objects.all())
tuteurs = list(Tuteur.objects.all())

STATUTS = ['pere', 'mere', 'autre']

for adh in adherents:
    # S'assurer que le tout premier tuteur est 'pere' ou 'mere'
    if tuteurs:
        premier_tuteur = choice(tuteurs)
        statut_initial = choice(['pere', 'mere'])
        SuiviTuteurAdherent.objects.create(
            adherent=adh,
            tuteur=premier_tuteur,
            statut=statut_initial
        )

    # Ajouter éventuellement 1 à 2 autres tuteurs 'autre'
    for _ in range(0, 2):
        tuteur_autre = choice(tuteurs)
        if tuteur_autre != premier_tuteur:
            SuiviTuteurAdherent.objects.create(
                adherent=adh,
                tuteur=tuteur_autre,
                statut='autre'
            )

print("✅ Suivis Tuteur-Adhérent créés avec succès !")
