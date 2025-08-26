from datetime import timedelta
from django.utils import timezone
from Gestion_personnel.operation.models import Operation
from referentiel.fonction.models import Fonction
from referentiel.organisation_unite.models import OrganisationUnite
from Gestion_personnel.employe.models import Employe

# 🔹 Récupérer des employés existants (liste)
employes = Employe.objects.filter(pk__in=[1, 2, 3])

# 🔹 Récupérer des fonctions existantes (liste)
fonctions = Fonction.objects.filter(pk__in=[1, 2])

# 🔹 Récupérer des unités organisationnelles existantes (liste)
organisations = OrganisationUnite.objects.filter(pk__in=[1, 2])

# 🔹 Créer 5 opérations de test
for i in range(1, 6):
    Operation.objects.create(
        date_debut=timezone.now() + timedelta(days=i),
        date_fin=timezone.now() + timedelta(days=i + 30),
        statut='confirme' if i % 2 == 0 else 'annule',
        numero_note=1000 + i,
        numero_fiche=2000 + i,
        type_operation='recrutement' if i % 2 == 0 else 'mutation',
        id_employe=employes[i % len(employes)],  # sélection cyclique dans la liste
        id_organisation_unite=organisations[i % len(organisations)],
        id_fonction=fonctions[i % len(fonctions)],
        id_employe_respensable=employes[1],      # fixe ou autre logique
        id_employe_enregitre=employes[2]         # fixe ou autre logique
    )

print("✅ 5 opérations créées avec succès !")
