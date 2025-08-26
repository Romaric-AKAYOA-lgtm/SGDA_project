from django.shortcuts import redirect
from django.utils.timezone import now
from django.urls import reverse
from .models import Activation
import re
import datetime


class ActivationMiddleware:
    """Middleware pour forcer l'activation avant l'accès au site."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Liste des pages exemptées de la vérification d'activation
        exempt_urls = [
            reverse("Activation:activation_page"),  # Page d'activation
            reverse("admin:index"),  # Interface d'administration
        ]

        # Exclure l'interface d'administration et la page d'activation de la vérification
        if not any(request.path.startswith(url) for url in exempt_urls):
            try:
                # Récupérer la dernière activation enregistrée
                activation = Activation.objects.latest("activated_on")

                # Si la clé d'activation est invalide, rediriger vers la page d'activation
                if not activation.is_valid():
                    return redirect(reverse("Activation:activation_page"))  # Redirige vers la page d'activation

                # Vérifier si la clé d'activation est présente dans les cookies ou la session
                activation_key = request.COOKIES.get('activation_key') or request.session.get('activation_key')

                if activation_key:
                    # Vérifier si la clé d'activation a le bon format
                    key_format = r'^[a-f0-9\-]{36}-\d{12}$'  # Format de clé attendu (ex : db128825-d8dd-4926-84bb-c3210fddb8c3-202504012252)
                    if not re.match(key_format, activation_key):
                        return redirect(reverse("Activation:activation_page"))  # Format invalide -> redirection

                    # Découper la clé pour extraire la date et l'heure d'expiration
                    expiration_date_str = activation_key.split('-')[-1]  # Récupérer la dernière partie de la clé (date et heure)
                    expiration_date = datetime.datetime.strptime(expiration_date_str, "%Y%m%d%H%M")  # Convertir la date en objet datetime

                    # Vérifier si la clé a expiré
                    if expiration_date < now():
                        return redirect(reverse("Activation:activation_page"))  # Redirige vers la page d'activation si la clé est expirée

            except Activation.DoesNotExist:
                # Aucun enregistrement trouvé → redirection vers la page d'activation
                return redirect(reverse("Activation:activation_page"))

        return self.get_response(request)
