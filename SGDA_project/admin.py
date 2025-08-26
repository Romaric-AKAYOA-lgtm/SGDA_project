from django.contrib import admin
from django.urls import path
from django.contrib.admin.sites import AlreadyRegistered

from Gestion_adherent.Inscription_adherent.adherent.models import Adherent
from Gestion_adherent.Inscription_adherent.suiviTuteurAdherent.models import SuiviTuteurAdherent
from Gestion_adherent.Inscription_adherent.tuteur.models import Tuteur
from Gestion_adherent.Prise_en_charge_adherent.models import PriseEnChargeAdherent

from .views_admin import  dashboard_view  # 🔁 Vue externe : dashboard

# Importation des modèles
from Gestion_personnel.absence.models import Absence

from Gestion_personnel.operation.models import Operation

from referentiel.fonction.models import Fonction
from referentiel.organisation_unite.models import OrganisationUnite
from referentiel.structure.models import Structure
from referentiel.unite.models import Unite


# 🔧 Création d’un site admin personnalisé
class MyAdminSite(admin.AdminSite):
    site_header = "Interface Admin INRAP"
    site_title = "INRAP Admin"
    index_title = "Bienvenue sur l'administration INRAP"

    def get_urls(self):
        urls = super().get_urls()
        # Vue personnalisée du tableau de bord
        custom_urls = [
            path(
                "dashboard/",
                self.admin_view(lambda request: dashboard_view(request, self)),
                name="dashboard"
            ),
        ]
        return custom_urls + urls


# 🎯 Instance de notre site personnalisé
admin_site = MyAdminSite(name='myadmin')

# 📦 Liste des modèles à enregistrer
modeles_a_enregistrer = [
    Structure,
    Fonction,
    Unite,
    OrganisationUnite,

    Operation,
    Absence,
    Tuteur,
    Adherent, 
    SuiviTuteurAdherent,
    PriseEnChargeAdherent
]

# 🔁 Enregistrement des modèles
for modele in modeles_a_enregistrer:
    try:
        admin_site.register(modele)
    except AlreadyRegistered:
        pass
