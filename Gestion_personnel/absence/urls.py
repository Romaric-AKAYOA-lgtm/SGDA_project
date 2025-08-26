from django.urls import path
from . import views

app_name = 'absence'

urlpatterns = [
    path('', views.absence_list, name='liste'),
    path('ajouter/', views.absence_create, name='ajouter'),
    path('modifier/<int:pk>/', views.absence_update, name='modifier'),
    path('rechercher/', views.absence_search, name='rechercher'),
    path('imprimer/', views.imprimer_toutes_les_absences, name='imprimer'),
    path('imprimer_absence/<int:id_absence>/', views.generer_pdf_absence, name='imprimer_absence'),
    # Pour imprimer TOUS les congés annuels
    path('imprimer_conges_annuels/', views.generer_pdf_conges_annuels, name='imprimer_conges_annuels'),
    # Ajout des URLs pour les autres documents PDF
    path('certificat-reprise-service/<int:id_absence>/', views.certificat_reprise_service, name='certificat_reprise_service'),
    path('attestation-cessation-service/<int:id_absence>/', views.attestation_cessation_service, name='attestation_cessation_service'),
    path('attestation-presence/<int:id_absence>/', views.attestation_presence, name='attestation_presence'),
]

