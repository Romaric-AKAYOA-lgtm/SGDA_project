from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import SuiviTuteurAdherent
from .forms import SuiviTuteurAdherentForm


# Liste des suivis Tuteur-Adhérent
def suivi_list(request):
    query = request.GET.get('q', '').strip()
    suivis_qs = SuiviTuteurAdherent.objects.all().order_by('-date_creation')

    if query:
        suivis_qs = suivis_qs.filter(
            Q(adherent__first_name__icontains=query) |
            Q(adherent__last_name__icontains=query) |
            Q(tuteur__first_name__icontains=query) |
            Q(tuteur__last_name__icontains=query)
        )

    paginator = Paginator(suivis_qs, 10)
    page_number = request.GET.get('page')
    suivis = paginator.get_page(page_number)

    return render(request, 'suiviTuteurAdherent/suivi_list.html', {
        'suivis': suivis,
        'query': query,
    })


# Création d'un suivi
def suivi_create(request):
    if request.method == 'POST':
        form = SuiviTuteurAdherentForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Suivi Tuteur-Adhérent enregistré avec succès.")
                if request.POST.get("action") == "save_and_new":
                    return redirect('suivi_tuteur:suivi_create')
                return redirect('suivi_tuteur:suivi_list')
            except ValueError as e:
                form.add_error(None, str(e))
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        form = SuiviTuteurAdherentForm()

    return render(request, 'suiviTuteurAdherent/suivi_form.html', {
        'form': form,
        'mode': 'ajouter',
    })


# Modification d'un suivi
def suivi_update(request, pk):
    suivi = get_object_or_404(SuiviTuteurAdherent, pk=pk)

    if request.method == 'POST':
        form = SuiviTuteurAdherentForm(request.POST, instance=suivi)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Suivi Tuteur-Adhérent mis à jour.")
                return redirect('suivi_tuteur:suivi_list')
            except ValueError as e:
                form.add_error(None, str(e))
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        form = SuiviTuteurAdherentForm(instance=suivi)

    return render(request, 'suiviTuteurAdherent/suivi_form.html', {
        'form': form,
        'mode': 'modifier',
        'suivi': suivi,
    })


# Recherche de suivi
def suivi_search(request):
    query = request.GET.get('q', '').strip()
    if query:
        suivis = SuiviTuteurAdherent.objects.filter(
            Q(adherent__first_name__icontains=query) |
            Q(adherent__last_name__icontains=query) |
            Q(tuteur__first_name__icontains=query) |
            Q(tuteur__last_name__icontains=query)
        ).order_by('-date_creation')
    else:
        suivis = SuiviTuteurAdherent.objects.all().order_by('-date_creation')

    return render(request, 'suiviTuteurAdherent/suivi_search.html', {
        'suivis': suivis,
        'query': query,
    })


# Archivage / désarchivage d'un suivi
def suivi_archive(request, pk):
    suivi = get_object_or_404(SuiviTuteurAdherent, pk=pk)
    # Ici tu peux décider si tu veux supprimer ou changer un statut "actif/inactif"
    suivi.delete()
    messages.success(request, "Suivi Tuteur-Adhérent supprimé avec succès.")
    return redirect('suivi_tuteur:suivi_list')


# Archivage / réactivation en groupe
def suivi_archive_group(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids')
        suivis = SuiviTuteurAdherent.objects.filter(id__in=ids)
        count = suivis.count()
        suivis.delete()
        messages.success(request, f"{count} suivi(s) supprimé(s) avec succès.")
    return redirect('suivi_tuteur:suivi_list')


# Impression / export PDF (exemple simple)
def suivi_print_detail(request, pk):
    suivi = get_object_or_404(SuiviTuteurAdherent, pk=pk)
    # Ici tu peux générer un PDF ou rendre un template prêt pour impression
    return render(request, 'suiviTuteurAdherent/suivi_print_detail.html', {
        'suivi': suivi,
    })


# Impression / export PDF liste
def suivi_print_list(request):
    suivis = SuiviTuteurAdherent.objects.all().order_by('-date_creation')
    return render(request, 'suiviTuteurAdherent/suivi_print_list.html', {
        'suivis': suivis,
    })
