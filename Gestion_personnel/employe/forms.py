import random
import string
from referentiel.personne.forms import PersonneForm
from .models import Employe
from django import forms
from django.contrib.auth import get_user_model

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

class EmployeForm(PersonneForm):
    class Meta(PersonneForm.Meta):
        model = Employe
        fields = PersonneForm.Meta.fields + ['grade', 'echelle', 'categorie']
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
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'statut_user': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'grade': forms.TextInput(attrs={'class': 'form-control'}),
            'echelle': forms.NumberInput(attrs={'class': 'form-control'}),
            'categorie': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.data:
            data = self.data.copy()

            first_name = data.get('first_name', '').strip()
            last_name = data.get('last_name', '').strip()
            date_naissance = data.get('date_naissance', '')
            year = date_naissance[:4] if date_naissance and len(date_naissance) >= 4 else 'XXXX'

            # Username unique
            if not data.get('username') and first_name and last_name:
                username = generate_unique_username(first_name, last_name, year)
                data['username'] = username

            # Password sécurisé
            if not data.get('password1') or not data.get('password2'):
                password = generate_random_password()
                data['password1'] = password
                data['password2'] = password

            # statut_user
            if not data.get('statut_user'):
                data['statut_user'] = 'employé(e)'

            self.data = data

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def clean_grade(self):
        grade = self.cleaned_data.get('grade')
        if not grade:
            raise forms.ValidationError('Le grade est obligatoire.')
        return grade

    def clean_echelle(self):
        echelle = self.cleaned_data.get('echelle')
        if echelle is None or echelle <= 0:
            raise forms.ValidationError('L\'échelle doit être un nombre positif.')
        return echelle

    def clean_categorie(self):
        categorie = self.cleaned_data.get('categorie')
        if not categorie:
            raise forms.ValidationError('La catégorie est obligatoire.')
        return categorie
