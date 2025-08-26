from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Cotisation
from .forms import CotisationForm
from datetime import datetime, timedelta

# Liste des cotisations
def cotisation_list(request):
    query = request.GET.get('q', '').strip()
    cotisations_qs = Cotisation.objects.filter(statut=Cotisation.STATUT_VALIDE)  # par défaut les valides

    if query:
        cotisations_qs = cotisations_qs.filter(
            Q(adherent__first_name__icontains=query) |
            Q(adherent__last_name__icontains=query) |
            Q(type_cotisation__icontains=query) |
            Q(montant__icontains=query)
        )

    cotisations_qs = cotisations_qs.order_by('-date_cotisation')
    paginator = Paginator(cotisations_qs, 10)
    page_number = request.GET.get('page')
    cotisations = paginator.get_page(page_number)

    return render(request, 'Cotisation_adherent/cotisation_list.html', {
        'cotisations': cotisations,
        'search_query': query,
    })


# Création d'une cotisation
def cotisation_create(request):
    if request.method == 'POST':
        form = CotisationForm(request.POST)
        if form.is_valid():
            cotisation = form.save(commit=False)
            # Définir le statut en fonction du type et montant
            cotisation.statut = Cotisation.STATUT_VALIDE if is_cotisation_valide(cotisation) else Cotisation.STATUT_INVALIDE
            cotisation.save()
            messages.success(request, "Cotisation enregistrée avec succès.")
            if request.POST.get("action") == "save_and_new":
                return redirect('cotisation:cotisation_create')
            return redirect('cotisation:cotisation_list')
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        form = CotisationForm()

    return render(request, 'Cotisation_adherent/cotisation_form.html', {
        'form': form,
        'mode': 'ajouter'
    })


# Modification d'une cotisation
def cotisation_update(request, pk):
    cotisation = get_object_or_404(Cotisation, pk=pk)

    if request.method == 'POST':
        form = CotisationForm(request.POST, instance=cotisation)
        if form.is_valid():
            cotisation = form.save(commit=False)
            cotisation.statut = Cotisation.STATUT_VALIDE if is_cotisation_valide(cotisation) else Cotisation.STATUT_INVALIDE
            cotisation.save()
            messages.success(request, "Cotisation mise à jour avec succès.")
            return redirect('cotisation:cotisation_list')
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        form = CotisationForm(instance=cotisation)

    return render(request, 'Cotisation_adherent/cotisation_form.html', {
        'form': form,
        'mode': 'modifier',
        'cotisation': cotisation
    })


# Archiver ou réactiver une cotisation
def cotisation_archive(request, pk):
    cotisation = get_object_or_404(Cotisation, pk=pk)
    if cotisation.statut == Cotisation.STATUT_INVALIDE:
        cotisation.statut = Cotisation.STATUT_VALIDE
        messages.success(request, "Cotisation réactivée avec succès.")
    else:
        cotisation.statut = Cotisation.STATUT_INVALIDE
        messages.success(request, "Cotisation archivée avec succès.")
    cotisation.save()
    return redirect('cotisation:cotisation_list')


# Archiver / réactiver en groupe
def cotisation_archive_group(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids')
        cotisations = Cotisation.objects.filter(id__in=ids)

        count_valide = 0
        count_invalide = 0

        for c in cotisations:
            if c.statut == Cotisation.STATUT_VALIDE:
                c.statut = Cotisation.STATUT_INVALIDE
                count_invalide += 1
            else:
                c.statut = Cotisation.STATUT_VALIDE
                count_valide += 1
            c.save()

        messages.success(request, f"{count_invalide} cotisation(s) archivée(s), {count_valide} cotisation(s) réactivée(s).")

    return redirect('cotisation:cotisation_list')


# Recherche
def cotisation_search(request):
    query = request.GET.get('q', '').strip()
    if query:
        cotisations = Cotisation.objects.filter(
            Q(adherent__first_name__icontains=query) |
            Q(adherent__last_name__icontains=query) |
            Q(type_cotisation__icontains=query) |
            Q(montant__icontains=query)
        ).order_by('-date_cotisation')
    else:
        cotisations = Cotisation.objects.all().order_by('-date_cotisation')

    return render(request, 'Cotisation_adherent/cotisation_search.html', {
        'cotisations': cotisations,
        'query': query
    })


# Impression de la liste
def cotisation_print_list(request):
    cotisations = Cotisation.objects.all().order_by('-date_cotisation')
    return render(request, 'Cotisation_adherent/cotisation_print_list.html', {'cotisations': cotisations})


# Impression détail
def cotisation_print_detail(request, pk):
    cotisation = get_object_or_404(Cotisation, pk=pk)
    return render(request, 'Cotisation_adherent/cotisation_print_detail.html', {'cotisation': cotisation})


def is_cotisation_valide(cotisation):
    """
    Retourne True si la cotisation est valide à l'instant t
    en utilisant directement les attributs de l'instance.
    """
    # Vérifier que le type de cotisation et le montant existent
    if not cotisation.type_cotisation or not cotisation.montant:
        return False

    # Vérifier la validité temporelle
    # On suppose que cotisation.type_cotisation.duree_validite existe en jours
    duree = getattr(cotisation.type_cotisation, 'duree_validite', 0)
    if duree == 0:
        return True  # Cotisation illimitée

    date_expiration = cotisation.date_cotisation + timedelta(days=duree)
    return datetime.now().date() <= date_expiration
