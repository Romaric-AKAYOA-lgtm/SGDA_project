from django import forms
from django.utils.timezone import now
from .models import Activation
import uuid
from datetime import timedelta

class ActivationForm(forms.ModelForm):
    class Meta:
        model = Activation
        fields = ['key', 'expires_on']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk and not self.instance.expires_on:
            self.fields['expires_on'].initial = now() + timedelta(days=90)

        if not self.instance.pk and not self.instance.key:
            self.fields['key'].initial = self.generate_activation_key()  # Proposer une clé UUID

        if self.instance.pk:
            self.fields['key'].widget.attrs['readonly'] = True

    def generate_activation_key(self):
        # Générer la clé au format UUID-YYYYMMDDHHMM
        uuid_part = str(uuid.uuid4())
        expiration_date = now() + timedelta(days=90)  # Utiliser la date d'expiration actuelle ou celle définie
        expiration_str = expiration_date.strftime("%Y%m%d%H%M")  # Format: YYYYMMDDHHMM
        return f"{uuid_part}-{expiration_str}"

    def clean_expires_on(self):
        expires_on = self.cleaned_data.get('expires_on')
        if expires_on <= now():
            raise forms.ValidationError("La date d'expiration doit être dans le futur.")
        return expires_on

    def save(self, commit=True):
        if not self.instance.key:
            self.instance.key = self.generate_activation_key()  # Générer la clé UUID-YYYYMMDDHHMM
        return super().save(commit)


class ActivationKeyForm(forms.Form):
    key = forms.RegexField(
        regex=r'^[a-f0-9\-]{36}-\d{12}$',  # Regex pour vérifier UUID-YYYYMMDDHHMM
        max_length=49,
        label="Clé d'activation",
        error_messages={'invalid': "Format invalide. Le format attendu est XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-YYYYMMDDHHMM."}
    )
