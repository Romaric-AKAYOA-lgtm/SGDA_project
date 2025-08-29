import os
import django
from random import choice, randint
from django.utils import timezone
from datetime import timedelta

# ⚠️ Adapter au chemin de ton projet
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Gestion_Personnel_Visites_INRAP.settings")
django.setup()

from Gestion_adherent.Inscription_adherent.adherent.models import Adherent
from Gestion_personnel.operation.models import Operation
from Gestion_adherent.Prise_en_charge_adherent.models import PriseEnChargeAdherent

# Supprimer les prises en charge existantes (optionnel)
PriseEnChargeAdherent.objects.all().delete()

adherents = list(Adherent.objects.all())
operations = list(Operation.objects.all())

if not adherents or not operations:
    print("⚠️ Il faut au moins un adhérent et une opération dans la base.")
else:
    for i in range(1, 1001):  # exemple : créer 50 prises en charge
        adherent = choice(adherents)
        operation = choice(operations)

        # Décider aléatoirement si opération médecin est renseignée
        avec_medecin = choice([True, False])

        if avec_medecin:
            operation_medecin = choice(operations)
            nom_medecin = f"Dr. Medecin{i}"
            fonction_medecin = f"Fonction{i%5 + 1}"
        else:
            operation_medecin = None
            nom_medecin = f"Dr. Medecin{i}"
            fonction_medecin = f"Fonction{i%5 + 1}"

        prise = PriseEnChargeAdherent.objects.create(
            objet=f"Objet de la prise en charge {i}",
            description=f"Description de la prise en charge {i}",
            date_creation=timezone.now() - timedelta(days=randint(0, 30)),
            adherent=adherent,
            operation_enregistrer=operation,
            operation_medecin=operation_medecin,
            nom_complet_medecin=nom_medecin if not operation_medecin else None,
            fonction_medecin=fonction_medecin if not operation_medecin else None,
            specialite_medecin=f"Specialite{i%3 + 1}" if avec_medecin else None
        )

        print(i, f"✅ Prise en charge créée : {prise}")

print(i, "🎉 Toutes les prises en charge ont été générées avec succès !")
