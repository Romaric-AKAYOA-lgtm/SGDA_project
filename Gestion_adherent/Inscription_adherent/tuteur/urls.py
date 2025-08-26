from django.urls import path
from . import views, vew_print

app_name = 'tuteur'
 
urlpatterns = [
    path('', views.tuteur_list, name='tuteur_list'),  # Consulter la liste des tuteurs
    path('nouveau/', views.tuteur_create, name='tuteur_create'),  # Enregistrer un nouveau tuteur
    path('rechercher/', views.tuteur_search, name='tuteur_search'),  # Rechercher un tuteur
    path('modifier/<int:pk>/', views.tuteur_update, name='tuteur_update'),  # Modifier un tuteur
    path('archiver-groupe/', views.tuteur_archive_group, name='tuteur_archive_group'),  # Archiver un groupe de tuteurs
    path('archiver/<int:pk>/', views.tuteur_archive, name='tuteur_archive'),  # Archiver un tuteur
     
    # Impression
    path('imprimer/<int:pk>/', vew_print.tuteur_print_detail, name='tuteur_print'),  # Imprimer fiche individuelle
    path('imprimer-liste/', vew_print.tuteur_print_list, name='tuteur_print_list'),  # Imprimer liste des tuteurs
    path('imprimer/<int:pk>/', vew_print.tuteur_print_detail, name='tuteur_print_detail'),
    path('imprimer-operation/<int:pk>/', vew_print.tuteur_print_list_operation, name='tuteur_print_list_operatrion'),
]
