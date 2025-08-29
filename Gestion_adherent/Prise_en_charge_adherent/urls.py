from django.urls import path
from . import views

app_name = "prise_en_charge"

urlpatterns = [
    # Liste des prises en charge
    path('', views.prise_en_charge_list, name='list'),

    # Création d'une prise en charge
    path('create/', views.prise_en_charge_create, name='create'),

    # Modification d'une prise en charge
    path('update/<int:pk>/', views.prise_en_charge_update, name='update'),

    # Détail d'une prise en charge
    path('detail/<int:pk>/', views.prise_en_charge_detail, name='detail'),

    # Suppression d'une prise en charge
    path('delete/<int:pk>/', views.prise_en_charge_delete, name='delete'),

    # Impression de la liste complète
    path('print-list/', views.prise_en_charge_print_list, name='print_list'),

    # Impression d'une prise en charge
    path('print-detail/<int:pk>/', views.prise_en_charge_print_detail, name='print_detail'),
]