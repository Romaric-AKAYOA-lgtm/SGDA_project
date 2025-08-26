
# context_processors.py

from .models import Structure

def administration(request):
    try:
        # Vous pouvez personnaliser la récupération de l'administration ici (par exemple, en prenant le premier objet)
        administration = Structure.objects.first()  # Ou votre logique spécifique pour obtenir l'objet administration
        return {'administration': administration}
    except Structure.DoesNotExist:
        return {'administration': None}
