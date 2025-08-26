from compte.simulateur_middleware import verifier_protection

def administration(request):
    """
    Context processor qui ajoute des infos sur l'utilisateur connecté et la protection de la page.
    """
    utilisateur_connecte = request.user.is_authenticated
    est_protege = verifier_protection(request.path, user=request.user)

    return {
        'est_protege': est_protege,
        'utilisateur_actuel': request.user if utilisateur_connecte else None,
        'utilisateur_connecte': utilisateur_connecte,
    }


import logging
from django.utils.timezone import now

logger = logging.getLogger('user_activity')

class UserActivityLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        user = request.user if request.user.is_authenticated else None
        username = user.username if user else 'Anonymous'
        last_login = user.last_login.isoformat() if user and user.last_login else 'N/A'

        logger.info(
            f"User: {username} | "
            f"Last login: {last_login} | "
            f"Path: {request.path} | "
            f"Method: {request.method} | "
            f"Timestamp: {now().isoformat()} | "
            f"Status Code: {response.status_code}"
        )

        return response
