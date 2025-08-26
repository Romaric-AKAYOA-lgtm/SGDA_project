from django.contrib import admin
from django.urls import path, include
from . import views
from .admin import admin_site  # custom admin site
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('base/', views.base_html),  # ouvre base.html
    path('admin/', admin.site.urls),
    path('myadmin/', include((admin_site.get_urls(), 'myadmin'), namespace='myadmin')),

    path('Activation/', include('Activation.urls')),
    path('compte/', include('compte.urls', namespace='compte')),
    path('unites/', include(('referentiel.unite.urls', 'unite'), namespace='unite')),
    path('fonctions/', include(('referentiel.fonction.urls', 'fonction'), namespace='fonction')),
    path('referentiel/', include('referentiel.urls', namespace='referentiel')),
    path('Gestion_personnel/', include('Gestion_personnel.urls')),

    path('organisations_unites/', include(('referentiel.organisation_unite.urls', 'organisation_unite'), namespace='organisation_unite')),
    path('structures/', include(('referentiel.structure.urls', 'structure'), namespace='structure')),
    path('employes/', include(('Gestion_personnel.employe.urls', 'employe'), namespace='employe')),
    path('operation/', include(('Gestion_personnel.operation.urls', 'operation'), namespace='operation')),
    path('absence/', include(('Gestion_personnel.absence.urls', 'absence'), namespace='absence')),

    path('Gestion_adherent/', include(('Gestion_adherent.urls', 'tuteur'))),
    path('tuteur/', include(('Gestion_adherent.Inscription_adherent.tuteur.urls', 'tuteur'), namespace='tuteur')),
    path('adherent/', include(('Gestion_adherent.Inscription_adherent.adherent.urls', 'adherent'), namespace='adherent')),
    path('suivi-tuteur-adherent/',include(('Gestion_adherent.Inscription_adherent.suiviTuteurAdherent.urls', 'suivi_tuteur_adherent'),namespace='suivi_tuteur_adherent')),

    path('prise-en-charge-adherent/', include(('Gestion_adherent.Prise_en_charge_adherent.urls', 'prise_en_charge_adherent'), namespace='prise_en_charge_adherent')),
    path('cotisation/', include(('Gestion_adherent.Cotisation_adherent.urls', 'cotisation'), namespace='cotisation')),
    #path('inscription-adherent/', include(('Gestion_adherent.inscription_adherent.urls', 'inscription_adherent'), namespace='inscription_adherent')),
    path('', views.home_view, name='home'),
]

# Gestion des fichiers média
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Reload pour DEBUG uniquement
if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
