from referentiel.structure.models import Structure
from referentiel.unite.models import Unite
from referentiel.organisation_unite.models import OrganisationUnite

# Récupère la structure existante (id=1)
structure = Structure.objects.get(pk=1)

# Liste des unités avec désignations plus courtes
unites_hierarchie = [
    ("Direction Générale", 1),
    ("Service Informatique", 2),
    ("Division Réseaux", 3),
    ("Section Support", 4)
]

parent_org = None
for nom, unite_id in unites_hierarchie:
    unite = Unite.objects.get(pk=unite_id)
    designation = f"Organisation {nom}"

    # ⚠️ Respecte le max_length du modèle (30)
    designation = designation[:30]

    org = OrganisationUnite.objects.create(
        designation=designation,
        organisation_unite_parent=parent_org,
        unite=unite,
        structure=structure
    )
    parent_org = org  # le suivant sera enfant de celui-ci

print("✅ Hiérarchie organisationnelle créée avec succès !")
