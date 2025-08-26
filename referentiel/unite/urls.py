from django.urls import path
from . import views, vew_print

app_name = 'unite'  # ← ceci est important !

urlpatterns = [
    path('', views.unite_list, name='liste'),
    path('ajouter/', views.unite_create, name='ajouter'),
    path('modifier/<int:pk>/', views.unite_update, name='modifier'),
    path('rechercher/', views.unite_search, name='rechercher'),
    path('imprimer/', vew_print.unite_print, name='imprimer'),
]