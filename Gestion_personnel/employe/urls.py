from django.urls import path
from . import views, vew_print

app_name = 'employe'

urlpatterns = [
    path('', views.employe_list, name='employe_list'),  # Consulter les informations des employés (liste)
    path('nouveau/', views.employe_create, name='employe_create'),  # Enregistrer un nouvel employé
    path('rechercher/', views.employe_search, name='employe_search'),  # Rechercher un employé
    path('modifier/<int:pk>/', views.employe_update, name='employe_update'),  # Modifier un employé
    path('archiver-groupe/', views.employe_archive_group, name='employe_archive_group'),  # Archiver un groupe d’employés
    path('archiver/<int:pk>/', views.employe_archive, name='employe_archive'),  # Archiver un employé
    path('imprimer/<int:pk>/', vew_print.employe_print_detail, name='employe_print'),  # Imprimer fiche individuelle
    path('imprimer-liste/', vew_print.employe_print_list, name='employe_print_list'),  # Imprimer liste des employés
    path('imprimer/<int:pk>/', vew_print.employe_print_detail, name='employe_print_detail'),
    path('imprimer-operation/<int:pk>/', vew_print.employe_print_list_operation, name='employe_print_list_operatrion'),
]