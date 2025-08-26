from referentiel.structure.models import Structure
from referentiel.unite.models import Unite
from referentiel.organisation_unite.models import OrganisationUnite

# Récupère la structure existante (id=1)
structure = Structure.objects.get(pk=1)

# Récupère les unités existantes par ID
direction = Unite.objects.get(pk=1)   # Direction Générale
service   = Unite.objects.get(pk=2)   # Service Informatique
division  = Unite.objects.get(pk=3)   # Division Réseaux
section   = Unite.objects.get(pk=4)   # Section Support

# Organisation racine
org_direction = OrganisationUnite.objects.create(
    designation="Organisation Direction Générale",
    unite=direction,
    structure=structure
)

# Organisation enfant (Service)
org_service = OrganisationUnite.objects.create(
    designation="Organisation Service Informatique",
    organisation_unite_parent=org_direction,
    unite=service,
    structure=structure
)

# Organisation enfant (Division)
org_division = OrganisationUnite.objects.create(
    designation="Organisation Division Réseaux",
    organisation_unite_parent=org_service,
    unite=division,
    structure=structure
)

# Organisation enfant (Section)
org_section = OrganisationUnite.objects.create(
    designation="Organisation Section Support",
    organisation_unite_parent=org_division,
    unite=section,
    structure=structure
)
