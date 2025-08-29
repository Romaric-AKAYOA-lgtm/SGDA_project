import os
import django
from random import choice, randint
from decimal import Decimal
from django.utils import timezone

# ⚠️ Adapter au chemin de ton projet
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Gestion_Personnel_Visites_INRAP.settings")
django.setup()

from Gestion_adherent.Inscription_adherent.adherent.models import Adherent
from Gestion_personnel.operation.models import Operation
from Gestion_adherent.Cotisation_adherent.models import Cotisation

# Supprimer les cotisations existantes (optionnel)
Cotisation.objects.all().delete()

# Récupérer tous les adhérents et opérations
adherents = list(Adherent.objects.all())
operations = list(Operation.objects.all())

TYPE_CHOICES = ['annuelle', 'mensuelle', 'ponctuelle']

for adh in adherents:
    if not operations:
        print("⚠️ Pas d'opération disponible pour les cotisations.")
        break

    operation = choice(operations)
    type_cotis = choice(TYPE_CHOICES)

    # Déterminer un montant minimal selon le type
    if type_cotis == 'annuelle':
        montant = Decimal(randint(100, 500))  # ≥100
    elif type_cotis == 'mensuelle':
        montant = Decimal(randint(10, 50))    # ≥10
    else:  # ponctuelle
        montant = Decimal(randint(1, 100))    # >0

    cotisation = Cotisation.objects.create(
        adherent=adh,
        operation=operation,
        montant=montant,
        type_cotisation=type_cotis
    )

    print(f"✅ Cotisation créée : {cotisation}")

print("🎉 Toutes les cotisations ont été générées avec succès !")
