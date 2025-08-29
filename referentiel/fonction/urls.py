from django.urls import path
from . import views, vew_print

app_name = 'fonction'  # ← Nom de l’espace de noms

urlpatterns = [
    path('', views.fonction_list, name='liste'),
    path('ajouter/', views.fonction_create, name='ajouter'),
    path('modifier/<int:pk>/', views.fonction_update, name='modifier'),
    path('rechercher/', views.fonction_search, name='rechercher'),
    path('imprimer/', vew_print.fonction_print, name='imprimer'),
    path('imprimer_hierarchique /', vew_print.fonction_print_hierarchique, name='imprimer_hierarchique_fonction'),
]
