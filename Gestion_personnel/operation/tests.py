import os
import django
from datetime import timedelta
from django.utils import timezone

# ⚠️ Adapter le chemin de ton settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monprojet.settings")
django.setup()

from Gestion_personnel.operation.models import Operation
from Gestion_personnel.employe.models import Employe
from referentiel.fonction.models import Fonction
from referentiel.organisation_unite.models import OrganisationUnite

# 🔹 Récupérer des employés existants
employes = list(Employe.objects.all()[:3])  # prends les 3 premiers employés
if len(employes) < 3:
    raise ValueError("❌ Il faut au moins 3 employés pour créer des opérations de test.")

# 🔹 Récupérer des fonctions existantes
fonctions = list(Fonction.objects.all()[:2])
if len(fonctions) < 2:
    raise ValueError("❌ Il faut au moins 2 fonctions pour créer des opérations de test.")

# 🔹 Récupérer des unités organisationnelles existantes
organisations = list(OrganisationUnite.objects.all()[:2])
if len(organisations) < 2:
    raise ValueError("❌ Il faut au moins 2 unités organisationnelles pour créer des opérations de test.")

# 🔹 Créer 5 opérations de test
for i in range(100, 500):
    Operation.objects.create(
        date_debut=timezone.now() + timedelta(days=i),
        date_fin=timezone.now() + timedelta(days=i + 30),
        statut='confirme' if i % 2 == 0 else 'annule',
        numero_note=1000 + i,
        numero_fiche=2000 + i,
        type_operation='affectation' if i % 2 == 0 else 'mutation',
        id_employe=employes[i % len(employes)],
        id_organisation_unite=organisations[i % len(organisations)],
        id_fonction=fonctions[i % len(fonctions)],
        id_employe_responsable=employes[1],   # CORRIGÉ
        id_employe_enregistre=employes[2]     # vérifie aussi ce nom
    )


print( i ,"✅  opérations créées avec succès !")
