from django.urls import path
from . import views, vew_print

app_name = 'organisation_unite'  # Namespace pour l'application

urlpatterns = [
    path('', views.organisation_unite_list, name='liste'),
    path('ajouter/', views.organisation_unite_create, name='ajouter'),
    path('modifier/<int:pk>/', views.organisation_unite_update, name='modifier'),
    path('rechercher/', views.organisation_unite_search, name='rechercher'),
    path('imprimer/', vew_print.organisation_unite_print, name='imprimer'),
    path('imprimer_organisation_hierarchique/', vew_print.organisation_print_hierarchique, name='imprimer_organisation_hierarchique'),
]
