from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse

from compte.middleware import LoginRequiredMiddleware


def verifier_protection(path="/dashboard/", user=None):
    """
    Vérifie si la page demandée est protégée par authentification.
    Retourne True si une redirection est effectuée (donc utilisateur non connecté et accès refusé).
    """
    factory = RequestFactory()
    request = factory.get(path)
    request.user = user or AnonymousUser()  # Par défaut : non connecté

    # Middleware avec réponse factice
    middleware = LoginRequiredMiddleware(lambda req: HttpResponse("OK"))
    response = middleware(request)

    # Une redirection signifie que la page est protégée
    return response.status_code == 302


# Test local uniquement
if __name__ == "__main__":
    is_protected = verifier_protection("/dashboard/")
    print("Page protégée ?" , "Oui" if is_protected else "Non")
