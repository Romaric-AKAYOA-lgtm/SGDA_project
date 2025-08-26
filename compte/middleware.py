from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from Activation.activation_middleware import ActivationMiddleware

EXEMPT_URLS = [
    reverse('compte:login'),
    reverse('compte:logout'),
]

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.timeout = 5 * 60  # 5 minutes

    def __call__(self, request):
        path = request.path_info

        if any(path.startswith(url) for url in EXEMPT_URLS):
            return self.get_response(request)

        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)

        # Vérifier que la session existe avant d'utiliser ActivationMiddleware
        if hasattr(request, 'session'):
            # Appel à ActivationMiddleware uniquement ici
            activation = ActivationMiddleware(self.get_response)
            return activation(request)

        return self.get_response(request)
