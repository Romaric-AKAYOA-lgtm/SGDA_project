# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from Gestion_adherent.Inscription_adherent.tuteur.models import Tuteur

from .models import Adherent
from .forms import AdherentForm


# Liste des adhérents (avec pagination)
def adherent_list(request):
    query = request.GET.get('q', '').strip()
    adherents_qs = Adherent.objects.filter(statut=Adherent.STATUT_ACTIF)

    if query:
        adherents_qs = adherents_qs.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(matricule__icontains=query) |
            Q(telephone__icontains=query) |
            Q(email__icontains=query) |
            Q(adresse__icontains=query)
        )

    adherents_qs = adherents_qs.order_by('-date_creation')
    paginator = Paginator(adherents_qs, 10)
    page_number = request.GET.get('page')
    adherents = paginator.get_page(page_number)

    return render(request, 'adherent/adherent_list.html', {
        'adherents': adherents,
        'search_query': query,
    })


# Définition des champs

def get_champs_adherent():
    # Onglet informations personnelles
    champs_personnels = [
        'first_name', 'last_name', 'date_naissance', 'lieu_naissance',
        'sexe', 'image'
    ]
    # Onglet coordonnées
    champs_contact = [
        'telephone', 'email', 'adresse'
    ]
    # Onglet parents
    champs_parents = ['pere', 'mere']
    # Onglet professionnels
    champs_professionnels = ['matricule', 'statut']

    return champs_personnels, champs_contact, champs_parents, champs_professionnels

# Création d’un adhérent
def adherent_create(request):
    champs_personnels, champs_contact, champs_parents, champs_professionnels = get_champs_adherent()

    if request.method == 'POST':
        form = AdherentForm(request.POST, request.FILES)
        if form.is_valid():
            matricule = form.cleaned_data.get('matricule')
            if Adherent.objects.filter(matricule=matricule).exists():
                form.add_error('matricule', 'Un adhérent avec ce matricule existe déjà.')
            else:
                form.save()
                messages.success(request, "Adhérent enregistré avec succès.")
                if request.POST.get("action") == "save_and_new":
                    return redirect('adherent:adherent_create')
                return redirect('adherent:adherent_list')
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        form = AdherentForm()

    return render(request, 'adherent/adherent_form.html', {
        'form': form,
        'mode': 'ajouter',
        'champs_personnels': champs_personnels,
        'champs_contact': champs_contact,
        'champs_parents': champs_parents,
        'champs_professionnels': champs_professionnels,
    })


# Modification d’un adhérent
def adherent_update(request, pk):
    champs_personnels, champs_contact, champs_parents, champs_professionnels = get_champs_adherent()
    adherent = get_object_or_404(Adherent, pk=pk)

    if request.method == 'POST':
        form = AdherentForm(request.POST, request.FILES, instance=adherent)
        if form.is_valid():
            form.save()
            messages.success(request, "Informations de l'adhérent mises à jour.")
            return redirect('adherent:adherent_list')
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        form = AdherentForm(instance=adherent)

    return render(request, 'adherent/adherent_form.html', {
        'form': form,
        'mode': 'modifier',
        'adherent': adherent,
        'champs_personnels': champs_personnels,
        'champs_contact': champs_contact,
        'champs_parents': champs_parents,
        'champs_professionnels': champs_professionnels,
    })


# Recherche
def adherent_search(request):
    query = request.GET.get('q', '').strip()

    if query:
        adherents = Adherent.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(matricule__icontains=query) |
            Q(telephone__icontains=query) |
            Q(email__icontains=query) |
            Q(adresse__icontains=query)
        ).order_by('-date_creation')
    else:
        adherents = Adherent.objects.all().order_by('-date_creation')

    return render(request, 'adherent/adherent_search.html', {
        'adherents': adherents,
        'query': query,
    })


# Archiver ou réactiver un adhérent
def adherent_archive(request, pk):
    adherent = get_object_or_404(Adherent, pk=pk)

    if adherent.statut == Adherent.STATUT_INACTIF:
        adherent.statut = Adherent.STATUT_ACTIF
        adherent.save()
        messages.success(request, f"Adhérent {adherent.matricule} réactivé avec succès.")
    else:
        adherent.statut = Adherent.STATUT_INACTIF
        adherent.save()
        messages.success(request, f"Adhérent {adherent.matricule} archivé avec succès.")

    return redirect('adherent:adherent_list')


# Archiver / réactiver en groupe
def adherent_archive_group(request):
    if request.method == 'POST':
        matricules = request.POST.getlist('matricules')
        adherents = Adherent.objects.filter(matricule__in=matricules)

        count_activés = 0
        count_archivés = 0

        for adh in adherents:
            if adh.statut == Adherent.STATUT_ACTIF:
                adh.statut = Adherent.STATUT_INACTIF
                count_archivés += 1
            else:
                adh.statut = Adherent.STATUT_ACTIF
                count_activés += 1
            adh.save()

        messages.success(
            request,
            f"{count_archivés} adhérent(s) archivé(s), {count_activés} adhérent(s) réactivé(s)."
        )

    return redirect('adherent:adherent_list')
