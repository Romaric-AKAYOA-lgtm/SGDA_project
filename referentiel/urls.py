from django.urls import path
from . import views

app_name = 'referentiel'  # ← ceci est important !

urlpatterns = [
    path('', views.referentiel_view, name='home_referentiel'),

]