from django.urls import path
from . import views

app_name = 'Gestion_adherent'  # ← ceci est important !

urlpatterns = [
    path('', views.Gestion_adherent_view, name='home_Gestion_adherent'),
    path('statistique_adherent/', views.statistic_adherent_view, name='statistique_adherents'),
] 