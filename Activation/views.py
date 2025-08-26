from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Activation
from .forms import ActivationKeyForm
from django.views.decorators.csrf import csrf_protect

def activation_view(request):
    """Page d'activation"""
    return render(request, "Activation/activation.html")


@csrf_protect
def activation_page(request):
    """Page pour entrer la clé d'activation"""
    error_message = None

    if request.method == "POST":
        form = ActivationKeyForm(request.POST)
        if form.is_valid():
            key = form.cleaned_data['key']
            try:
                # Rechercher l'activation correspondant à la clé
                activation = Activation.objects.get(key=key)
                if activation.is_valid():
                    # Si la clé est valide, rediriger l'utilisateur
                    return redirect(reverse('compte:logout'))  # Ou vers une autre page, selon votre logique
                else:
                    error_message = "Clé d'activation expirée."
            except Activation.DoesNotExist:
                error_message = "Clé d'activation invalide."

    else:
        form = ActivationKeyForm()

    return render(request, "Activation/activation.html", {
        "form": form,
        "error": error_message
    })