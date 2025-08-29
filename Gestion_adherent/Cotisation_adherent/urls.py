from django.urls import path
from . import views

app_name = 'cotisation'

urlpatterns = [
    # Liste des cotisations
    path('', views.cotisation_list, name='cotisation_list'),

    # Création d'une cotisation
    path('create/', views.cotisation_create, name='cotisation_create'),

    # Modification d'une cotisation
    path('update/<int:pk>/', views.cotisation_update, name='cotisation_update'),

    # Suppression ou archivage d'une cotisation
    path('archive/<int:pk>/', views.cotisation_archive, name='cotisation_archive'),

    # Archivage / réactivation en groupe
    path('archive-group/', views.cotisation_archive_group, name='cotisation_archive_group'),

    # Recherche
    path('search/', views.cotisation_search, name='cotisation_search'),

    # Impression
    path('print-list/', views.cotisation_print_list, name='cotisation_print_list'),
    path('print-detail/<int:pk>/', views.cotisation_print_detail, name='cotisation_print_detail'),
] 