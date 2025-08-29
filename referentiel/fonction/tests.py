from datetime import datetime
from referentiel.structure.models import Structure
from referentiel.fonction.models import Fonction

# ⚠️ Récupère la structure cible (id=1 ici)
structure = Structure.objects.get(pk=1)

# Liste des niveaux hiérarchiques
fonctions_base = ["Directeur Général", "Chef de Service", "Chef de Division", "Chef de Section"]

# Supprimer les fonctions existantes pour éviter les doublons
Fonction.objects.all().delete()

parent = None

for i, base in enumerate(fonctions_base, start=1):
    # Ajouter un suffixe unique pour éviter la contrainte UNIQUE
    unique_suffix = datetime.now().strftime("%H%M%S%f")  # heures, minutes, secondes, microsecondes
    designation = f"{base} {i} {unique_suffix}"

    # Créer la fonction
    fonction = Fonction.objects.create(
        designation=designation,
        fonction_parent=parent,
        structure=structure
    )

    # Le parent de l'étape suivante sera cette fonction
    parent = fonction

print("✅ Hiérarchie de fonctions créée avec désignations uniques !")
