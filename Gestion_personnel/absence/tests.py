import os
import django
from datetime import timedelta
from django.utils import timezone

# ⚠️ Adapter le chemin vers ton settings Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monprojet.settings")
django.setup()

from Gestion_personnel.employe.models import Employe
from Gestion_personnel.operation.models import Operation
from Gestion_personnel.absence.models import Absence  # adapte selon ton app

# 🔹 Récupérer des employés existants
employes = list(Employe.objects.all()[:3])
if len(employes) < 3:
    raise ValueError("❌ Il faut au moins 3 employés pour créer des absences de test.")

# 🔹 Récupérer des opérations existantes
operations = list(Operation.objects.filter(type_operation='mutation')[:3])
if len(operations) < 3:
    raise ValueError("❌ Il faut au moins 3 opérations de type 'mutation' pour créer des absences de test.")

# 🔹 Créer 10 absences de test
for i in range(5000):
    Absence.objects.create(
        type_absence='conge_annuel' if i % 2 == 0 else 'absence_imprevue',
        statut='confirme' if i % 2 == 0 else 'en_cours',
        date_debut=timezone.now() + timedelta(days=i),
        duree=30 if i % 2 == 0 else 5,
        lieu=f"Bureau {i+1}",
        motif=f"Motif test {i+1}",
        numero_note=1000 + i,
        numero_fiche=2000 + i,
        id_absence_operation_employe=operations[i % len(operations)],
        id_absence_operation_employe_respensable=operations[(i+1) % len(operations)],
        id_absence_operation_employe_enregistre=operations[(i+2) % len(operations)],
    )

print(i, "✅ 10 absences créées avec succès !")
