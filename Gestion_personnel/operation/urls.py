from django.urls import path
from . import views, vew_print_document, vew_print

app_name = 'operation'  # ← ceci est important !

urlpatterns = [
    path('', views.operation_list, name='liste'),
    path('ajouter/', views.operation_create, name='ajouter'),
    path('modifier/<int:pk>/', views.operation_update, name='modifier'),
    path('rechercher/', views.operation_search, name='rechercher'),
    path('imprimer/<int:id_operation>/', views.generer_pdf_operation, name='imprimer'),
    path('certificat-prise-service/<int:id_operation>/', vew_print_document.certificat_prise_service, name='certificat_prise_service'),
    path('attestation-prise-service/<int:id_operation>/', vew_print_document.attestation_prise_service, name='attestation_prise_service'),
    path('attestation-presence/<int:id_operation>/', vew_print_document.attestation_presence, name='attestation_presence'),
    path('attestation-employeur/<int:id_operation>/', vew_print_document.attestation_employeur, name='attestation_employeur'),
    path('attestation-cessation/<int:id_operation>/', vew_print_document.attestation_cessation, name='attestation_cessation'),

            # urls.py
    path('imprimer/toutes/', vew_print_document.imprimer_toutes_operations, name='imprimer_toutes_operations'),
    path('imprimer/mois/', vew_print_document.imprimer_operations_mois, name='imprimer_operations_mois'),
    path('imprimer/annee/', vew_print_document.imprimer_operations_annee, name='imprimer_operations_annee'),
]




