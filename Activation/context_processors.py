from .models import Activation

def check_activation(request):
    """
    Ajoute une variable 'activation_invalid' au contexte si l'activation est absente ou invalide.
    """
    activation_invalid = True  # Valeur par défaut : invalide

    try:
        activation = Activation.objects.first()
        if activation and activation.is_valid():
            activation_invalid = False
    except Exception as e:
        # On loguerait éventuellement l'erreur ici si nécessaire
        pass

    return {'activation_invalid': activation_invalid}
