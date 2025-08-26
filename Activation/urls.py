from django.urls import path
from . import views

app_name = 'Activation'

urlpatterns = [
    path('', views.activation_view, name='activation'),  # Page d'activation
    path('page/', views.activation_page, name='activation_page'),  # Page pour entrer la clé d'activation
]
