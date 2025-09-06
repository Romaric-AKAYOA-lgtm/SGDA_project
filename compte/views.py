from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ObjectDoesNotExist

from .forms import LoginForm
from .forms_register import RegisterForm

from Gestion_personnel.employe.models import Employe
from Gestion_personnel.operation.models import Operation

# compte/utils.p
def get_employe_id_connecte(request):
    """
    Retourne l'ID de l'employé connecté si actif,
    sinon None.
    """
    if request.user.is_authenticated:
        try:
            employe = Employe.objects.get(id=request.user.id)  # user = employé
            if employe.statut != Employe.STATUT_ACTIF:
                # L'employé n'est pas actif
                return None
            return employe.id
        except Employe.DoesNotExist:
            return None
    return None


def get_employe_connecte(user):
    """
    Retourne l'objet Employe lié à l'utilisateur connecté.
    Lève une exception si aucun Employe n'est trouvé ou si l'employé n'est pas actif.
    """
    try:
        employe = Employe.objects.get(id=user.id)
        if employe.statut != Employe.STATUT_ACTIF:
            raise ObjectDoesNotExist("Cet employé n'est pas actif.")
        return employe
    except Employe.DoesNotExist:
        raise ObjectDoesNotExist("Aucun employé lié à cet utilisateur.")


@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = LoginForm(request.POST or None)
    error = None

    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(request, username=username, password=password)

        if user:
            try:
                login(request, user)

                # Superutilisateur
                if user.is_superuser:
                    return redirect('home')
                employe = Employe.objects.get(id=user.id)

                # Vérifier si l'employé est actif
                if employe.statut != Employe.STATUT_ACTIF:
                    messages.error(request, "Votre compte employé n'est pas actif.")
                    return redirect('compte:logout')



                now = timezone.now()

                # Vérifier la dernière mutation active
                derniere_mutation = (
                    Operation.objects.filter(
                        Q(id_employe=employe),
                        Q(type_operation='mutation'),
                        Q(date_debut__lte=now),
                        Q(date_fin__isnull=True) | Q(date_fin__gte=now)
                    ).order_by('-date_creation').first()
                )

                if not derniere_mutation:
                    messages.error(request, "Aucune mutation active trouvée.")
                    return redirect('compte:logout')

                fonction = derniere_mutation.id_fonction.designation.lower()

                if 'parti' in fonction:
                     get_employe_connecte(derniere_mutation.id_employe)
                     return redirect('Gestion_visite:home_Gestion_visite')
                elif 'personne' in fonction:
                    get_employe_connecte(derniere_mutation.id_employe)
                    return redirect('Gestion_personnel:home_Gestion_personnel')
                else:
                    messages.error(request, "Votre fonction ne vous donne pas accès à un module.")
                    return redirect('compte:logout')

            except Employe.DoesNotExist:
                messages.error(request, "Aucun employé lié à cet utilisateur.")
                return redirect('compte:logout')

        else:
            error = "Identifiants incorrects."

    return render(request, 'compte/login.html', {'form': form, 'error': error})

@csrf_protect
def logout_view(request):
    logout(request)
    request.session.flush()  # Supprime toutes les données de session
    return redirect('compte:login')  # Utilisation du namespace pour éviter les conflits

def register_view(request, pk):
    employe = get_object_or_404(Employe, pk=pk)

    if request.method == 'POST':
        form = RegisterForm(request.POST, instance=employe)  # instance pour update
        if form.is_valid():
            employe = form.save()
            login(request, employe)  # connecter l'utilisateur mis à jour
            return redirect(reverse('compte:login'))  # rediriger vers login avec namespace
    else:
        form = RegisterForm(instance=employe)

    return render(request, 'compte/register.html', {
        'form': form,
        'employe': employe,
    })
