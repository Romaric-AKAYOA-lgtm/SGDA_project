from django.urls import path
from . import views, vew_print

app_name = 'adherent'

urlpatterns = [
    path('', views.adherent_list, name='adherent_list'),  # Consulter la liste des adhérents
    path('nouveau/', views.adherent_create, name='adherent_create'),  # Enregistrer un nouvel adhérent
    path('rechercher/', views.adherent_search, name='adherent_search'),  # Rechercher un adhérent
    path('modifier/<int:pk>/', views.adherent_update, name='adherent_update'),  # Modifier un adhérent
    path('archiver-groupe/', views.adherent_archive_group, name='adherent_archive_group'),  # Archiver un groupe d’adhérents
    path('archiver/<int:pk>/', views.adherent_archive, name='adherent_archive'),  # Archiver un adhérent

    # Impression
    path('imprimer/<int:pk>/', vew_print.adherent_print_detail, name='adherent_print'),  # Imprimer fiche individuelle
    path('imprimer-liste/', vew_print.adherent_print_list, name='adherent_print_list'),  # Imprimer liste des adhérents
    path('imprimer/<int:pk>/', vew_print.adherent_print_detail, name='adherent_print_detail'),
    path('imprimer-operation/<int:pk>/', vew_print.adherent_print_list_operation, name='adherent_print_list_operatrion'),
]
