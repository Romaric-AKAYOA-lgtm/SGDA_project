from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import PriseEnChargeAdherent
from .forms import PriseEnChargeAdherentForm

# Liste des prises en charge
def prise_en_charge_list(request):
    query = request.GET.get('q', '').strip()
    prises = PriseEnChargeAdherent.objects.all().order_by('-date_creation')
    
    if query:
        prises = prises.filter(
            Q(objet__icontains=query) |
            Q(description__icontains=query) |
            Q(nom_complet_medecin__icontains=query) |
            Q(fonction_medecin__icontains=query) |
            Q(specialite_medecin__icontains=query)
        )
    
    return render(request, 'Prise_en_charge_adherent/prise_en_charge_list.html', {
        'prises': prises,
        'query': query
    })

# Création
def prise_en_charge_create(request):
    if request.method == 'POST':
        form = PriseEnChargeAdherentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Prise en charge enregistrée avec succès.")
            if request.POST.get('action') == 'save_and_new':
                return redirect('prise_en_charge:create')
            return redirect('prise_en_charge:list')
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        form = PriseEnChargeAdherentForm()

    return render(request, 'Prise_en_charge_adherent/prise_en_charge_form.html', {
        'form': form,
        'mode': 'ajouter'
    })

# Modification
def prise_en_charge_update(request, pk):
    prise = get_object_or_404(PriseEnChargeAdherent, pk=pk)
    
    if request.method == 'POST':
        form = PriseEnChargeAdherentForm(request.POST, instance=prise)
        if form.is_valid():
            form.save()
            messages.success(request, "Prise en charge mise à jour avec succès.")
            return redirect('prise_en_charge:list')
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        form = PriseEnChargeAdherentForm(instance=prise)

    return render(request, 'Prise_en_charge_adherent/prise_en_charge_form.html', {
        'form': form,
        'mode': 'modifier',
        'prise': prise
    })

# Détail
def prise_en_charge_detail(request, pk):
    prise = get_object_or_404(PriseEnChargeAdherent, pk=pk)
    return render(request, 'Prise_en_charge_adherent/prise_en_charge_detail.html', {
        'prise': prise
    })

# Suppression
def prise_en_charge_delete(request, pk):
    prise = get_object_or_404(PriseEnChargeAdherent, pk=pk)
    prise.delete()
    messages.success(request, "Prise en charge supprimée avec succès.")
    return redirect('prise_en_charge:list')

# Impression liste
def prise_en_charge_print_list(request):
    prises = PriseEnChargeAdherent.objects.all().order_by('-date_creation')
    return render(request, 'Prise_en_charge_adherent/prise_en_charge_print_list.html', {
        'prises': prises
    })

# Impression détail
def prise_en_charge_print_detail(request, pk):
    prise = get_object_or_404(PriseEnChargeAdherent, pk=pk)
    return render(request, 'Prise_en_charge_adherent/prise_en_charge_print_detail.html', {
        'prise': prise
    })
