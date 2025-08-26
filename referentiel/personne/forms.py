import random
import string
from datetime import date
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Personne

User = get_user_model()

def generate_random_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return ''.join(random.choice(chars) for _ in range(length))

def generate_unique_username(first_name, last_name, year):
    base_username = f"{first_name.lower().replace(' ', '')}.{last_name.lower().replace(' ', '')}_inrap_{year}"
    username = base_username
    suffix = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}_{suffix}"
        suffix += 1
    return username
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Personne  # Assure-toi que le modèle Personne est importé correctement
from django import forms

class PersonneForm(UserCreationForm):
    class Meta:
        model = Personne
        fields = [
            'username', 'password1', 'password2',
            'first_name', 'last_name', 'matricule',
            'date_naissance', 'lieu_naissance', 'sexe',
            'telephone', 'email', 'nationalite', 'adresse',
            'situation_matrimoniale', 'profession',  # ✅ Ajoutés ici
            'statut', 'statut_user', 'image'
        ]
        widgets = {
            'username': forms.HiddenInput(),
            'password1': forms.HiddenInput(),
            'password2': forms.HiddenInput(),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'matricule': forms.TextInput(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'lieu_naissance': forms.TextInput(attrs={'class': 'form-control'}),
            'sexe': forms.Select(attrs={'class': 'form-select'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'nationalite': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'situation_matrimoniale': forms.Select(attrs={'class': 'form-select'}),  # ✅ Ajout widget
            'profession': forms.TextInput(attrs={'class': 'form-control'}),          # ✅ Ajout widget
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'statut_user': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['statut_user'].initial = self.initial.get('statut_user', 'employé(e)')

        if self.data:
            data = self.data.copy()

            first_name = data.get('first_name', '').strip()
            last_name = data.get('last_name', '').strip()
            date_naissance = data.get('date_naissance', '')
            year = date_naissance[:4] if date_naissance and len(date_naissance) >= 4 else 'XXXX'

            # Générer username unique si non fourni
            if not data.get('username') and first_name and last_name:
                data['username'] = generate_unique_username(first_name, last_name, year)

            # Générer mot de passe sécurisé
            if not data.get('password1') or not data.get('password2'):
                pwd = generate_random_password()
                data['password1'] = pwd
                data['password2'] = pwd

            # Statut user par défaut
            if not data.get('statut_user'):
                data['statut_user'] = self.fields['statut_user'].initial

            self.data = data

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def clean_date_naissance(self):
        date_naissance = self.cleaned_data.get('date_naissance')
        if date_naissance:
            today = date.today()
            age = today.year - date_naissance.year - (
                (today.month, today.day) < (date_naissance.month, date_naissance.day)
            )
            if age < 0:
                raise forms.ValidationError("La personne doit avoir au moins 18 ans.")
        return date_naissance
