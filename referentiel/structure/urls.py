from django.urls import path
from . import views, vew_impression

app_name = 'structure'  # Namespace pour l'application

urlpatterns = [
    path('', views.structure_list, name='liste'),
    path('ajouter/', views.structure_create, name='ajouter'),
    path('rechercher/', views.structure_search, name='rechercher'),
    path('modifier/<int:pk>/', views.structure_update, name='modifier'),

    # Impression de la liste des structures
    path('imprimer/', vew_impression.generer_pdf_structure, name='imprimer'),

    # Impression des détails d'une structure spécifique
    path('imprimer/<int:pk>/', vew_impression.generer_pdf_structure_detail, name='imprimer_detail'),
]

  
