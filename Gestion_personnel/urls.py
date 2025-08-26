from django.urls import path
from . import views

app_name = 'Gestion_personnel'  # ← ceci est important !

urlpatterns = [
    path('', views.Gestion_personnel_view, name='home_Gestion_personnel'),
    path('statistique_employe/', views.statistic_personnel_view, name='statistique_personnel'),

]
