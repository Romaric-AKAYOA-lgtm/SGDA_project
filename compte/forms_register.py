from django import forms
from django.contrib.auth.forms import UserCreationForm
from Gestion_personnel.employe.models import Employe

class RegisterForm(UserCreationForm):
    class Meta:
        model = Employe
        fields = ['username', 'password1', 'password2']
        labels = {
            'username': "Nom d'utilisateur",
            'password1': "Mot de passe",
            'password2': "Confirmer le mot de passe",
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Entrez votre nom d'utilisateur",
                'autocomplete': 'username',
                'autofocus': True,
            }),
        }

    # Personnaliser les champs non liés au modèle (password1, password2)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre mot de passe',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmez votre mot de passe',
            'autocomplete': 'new-password',
        })
