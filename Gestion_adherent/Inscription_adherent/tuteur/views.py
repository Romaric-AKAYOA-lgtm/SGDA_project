# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q

from .models import Tuteur
from .forms import TuteurForm


# Liste des tuteurs (avec pagination)
def tuteur_list(request):
    query = request.GET.get('q', '').strip()

    # Filtrer uniquement les tuteurs actifs
    tuteurs_qs = Tuteur.objects.filter(statut=Tuteur.STATUT_ACTIF)

    if query:
        # Recherche sur plusieurs champs, mais seulement parmi les actifs
        tuteurs_qs = tuteurs_qs.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(matricule__icontains=query) |
            Q(lieu_naissance__icontains=query) |
            Q(telephone__icontains=query) |
            Q(email__icontains=query) |
            Q(nationalite__icontains=query) |
            Q(adresse__icontains=query) |
            Q(statut__icontains=query) |
            Q(statut_user__icontains=query) |
            Q(situation_matrimoniale__icontains=query) |
            Q(profession__icontains=query)
        )

    tuteurs_qs = tuteurs_qs.order_by('-date_creation')

    paginator = Paginator(tuteurs_qs, 10)
    page_number = request.GET.get('page')
    tuteurs = paginator.get_page(page_number)

    return render(request, 'tuteur/tuteur_list.html', {
        'tuteurs': tuteurs,
        'search_query': query,
    })


# Définition des champs pour onglets
def get_champs_tuteur():
    # Onglet informations personnelles
    champs_personnels = [
        'first_name', 'last_name', 'date_naissance', 'lieu_naissance',
        'sexe', 'nationalite', 'image', 'situation_matrimoniale', 'profession'
    ]

    # Onglet coordonnées
    champs_contact = [
        'telephone', 'email', 'adresse'
    ]

    # Champs professionnels
    champs_professionnels = [
        'matricule', 'statut', 'statut_user'
    ]

    return champs_personnels, champs_contact, champs_professionnels


# Création d’un tuteur
def tuteur_create(request):
    champs_personnels, champs_contact, champs_professionnels = get_champs_tuteur()

    if request.method == 'POST':
        form = TuteurForm(request.POST, request.FILES)
        if form.is_valid():
            # On supprime la vérification du matricule
            form.save()
            messages.success(request, "Tuteur enregistré avec succès.")
            if request.POST.get("action") == "save_and_new":
                return redirect('tuteur:tuteur_create')
            return redirect('tuteur:tuteur_list')
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        form = TuteurForm()

    return render(request, 'tuteur/tuteur_form.html', {
        'form': form,
        'mode': 'ajouter',
        'champs_personnels': champs_personnels,
        'champs_contact': champs_contact,
        'champs_professionnels': champs_professionnels
    })


# Modification d’un tuteur
def tuteur_update(request, pk):
    champs_personnels, champs_contact, champs_professionnels = get_champs_tuteur()
    tuteur = get_object_or_404(Tuteur, pk=pk)

    if request.method == 'POST':
        form = TuteurForm(request.POST, request.FILES, instance=tuteur)
        if form.is_valid():
            form.save()
            messages.success(request, "Informations du tuteur mises à jour.")
            return redirect('tuteur:tuteur_list')
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        form = TuteurForm(instance=tuteur)

    return render(request, 'tuteur/tuteur_form.html', {
        'form': form,
        'mode': 'modifier',
        'tuteur': tuteur,
        'champs_personnels': champs_personnels,
        'champs_contact': champs_contact,
        'champs_professionnels': champs_professionnels
    })


# Recherche
def tuteur_search(request):
    query = request.GET.get('q', '').strip()

    if query:
        tuteurs = Tuteur.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(matricule__icontains=query) |
            Q(lieu_naissance__icontains=query) |
            Q(telephone__icontains=query) |
            Q(email__icontains=query) |
            Q(nationalite__icontains=query) |
            Q(adresse__icontains=query) |
            Q(statut__icontains=query) |
            Q(statut_user__icontains=query) |
            Q(situation_matrimoniale__icontains=query) |
            Q(profession__icontains=query)
        ).order_by('-date_creation')
    else:
        tuteurs = Tuteur.objects.all().order_by('-date_creation')
    paginator = Paginator(tuteurs, 10)
    page_number = request.GET.get('page')
    tuteurs = paginator.get_page(page_number)
    return render(request, 'tuteur/tuteur_search.html', {
        'tuteurs': tuteurs,
        'query': query,
    })


# Archiver ou réactiver un tuteur
def tuteur_archive(request, pk):
    tuteur = get_object_or_404(Tuteur, pk=pk)

    if tuteur.statut == Tuteur.STATUT_INACTIF:
        tuteur.statut = Tuteur.STATUT_ACTIF
        tuteur.save()
        messages.success(request, f"Tuteur {tuteur.matricule} réactivé avec succès.")
    else:
        tuteur.statut = Tuteur.STATUT_INACTIF
        tuteur.save()
        messages.success(request, f"Tuteur {tuteur.matricule} archivé avec succès.")

    return redirect('tuteur:tuteur_list')


# Archiver / réactiver en groupe
def tuteur_archive_group(request):
    if request.method == 'POST':
        matricules = request.POST.getlist('matricules')
        tuteurs = Tuteur.objects.filter(matricule__in=matricules)

        count_activés = 0
        count_archivés = 0

        for tut in tuteurs:
            if tut.statut == Tuteur.STATUT_ACTIF:
                tut.statut = Tuteur.STATUT_INACTIF
                count_archivés += 1
            else:
                tut.statut = Tuteur.STATUT_ACTIF
                count_activés += 1
            tut.save()

        messages.success(
            request,
            f"{count_archivés} tuteur(s) archivé(s), {count_activés} tuteur(s) réactivé(s)."
        )

    return redirect('tuteur:tuteur_list')
