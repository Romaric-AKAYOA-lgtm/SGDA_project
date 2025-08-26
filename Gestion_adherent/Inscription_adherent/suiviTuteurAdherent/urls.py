from django.urls import path
from . import views

app_name = 'suivi_tuteur'

urlpatterns = [
    # Liste des suivis
    path('', views.suivi_list, name='suivi_list'),

    # Création d'un suivi tuteur-adhérent
    path('create/', views.suivi_create, name='suivi_create'),

    # Modification d'un suivi
    path('update/<int:pk>/', views.suivi_update, name='suivi_update'),

    # Archivage / suppression d'un suivi
    path('archive/<int:pk>/', views.suivi_archive, name='suivi_archive'),

    # Archivage / réactivation en groupe
    path('archive-group/', views.suivi_archive_group, name='suivi_archive_group'),

    # Recherche de suivi
    path('search/', views.suivi_search, name='suivi_search'),

    # Impression / export PDF d'un suivi
    path('print/<int:pk>/', views.suivi_print_detail, name='suivi_print_detail'),
    path('print-list/', views.suivi_print_list, name='suivi_print_list'),
]
 