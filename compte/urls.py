from django.urls import path
from  compte  import views

app_name = 'compte'  # <- Déclaration du namespace

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/<int:pk>/', views.register_view, name='register'),
]
