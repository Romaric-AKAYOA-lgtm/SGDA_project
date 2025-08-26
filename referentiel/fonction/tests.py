from referentiel.structure.models import Structure
from referentiel.fonction.models import Fonction

# On récupère la structure avec id=1
structure = Structure.objects.get(pk=1)

# Fonction racine
direction = Fonction.objects.create(designation="Directeur Général", structure=structure)

# Fonction enfant (Service)
chef_service = Fonction.objects.create(designation="Chef de Service", fonction_parent=direction, structure=structure)

# Fonction enfant (Division)
chef_division = Fonction.objects.create(designation="Chef de Division", fonction_parent=chef_service, structure=structure)

# Fonction enfant (Section)
chef_section = Fonction.objects.create(designation="Chef de Section", fonction_parent=chef_division, structure=structure)
