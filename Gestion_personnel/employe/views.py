# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q

from .models import Employe
from .forms import EmployeForm

# Liste des employés (avec pagination)
from django.core.paginator import Paginator
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Employe

def employe_list(request):
    query = request.GET.get('q', '').strip()

    # Filtrer uniquement les employés actifs
    employes_qs = Employe.objects.filter(statut=Employe.STATUT_ACTIF)

    if query:
        # Recherche sur plusieurs champs, y compris statut, mais seulement parmi les actifs
        employes_qs = employes_qs.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(matricule__icontains=query) |
            Q(lieu_naissance__icontains=query) |
            Q(telephone__icontains=query) |
            Q(email__icontains=query) |
            Q(nationalite__icontains=query) |
            Q(statut__icontains=query) |
            Q(statut_user__icontains=query) |
            Q(grade__icontains=query) |
            Q(echelle__icontains=query) |
            Q(categorie__icontains=query)
        )

    employes_qs = employes_qs.order_by('-date_creation')

    paginator = Paginator(employes_qs, 10)
    page_number = request.GET.get('page')
    employes = paginator.get_page(page_number)

    return render(request, 'employe/employe_list.html', {
        'employes': employes,
        'search_query': query,
    })

# views.py
def get_champs_employe():
    champs_personnels = [
        'first_name', 'last_name', 'date_naissance', 'lieu_naissance',
        'sexe', 'telephone', 'email', 'nationalite', 'image'
    ]
    champs_professionnels = [
        'matricule', 'statut', 'grade', 'echelle', 'categorie'
    ]
    return champs_personnels, champs_professionnels

def employe_create(request):
    champs_personnels, champs_professionnels = get_champs_employe()
    if request.method == 'POST':
        form = EmployeForm(request.POST, request.FILES)
        if form.is_valid():
            matricule = form.cleaned_data.get('matricule')
            if Employe.objects.filter(matricule=matricule).exists():
                form.add_error('matricule', 'Un employé avec ce matricule existe déjà.')
            else:
                form.save()
                messages.success(request, "Employé enregistré avec succès.")
                if request.POST.get("action") == "save_and_new":
                    return redirect('employe:employe_create')
                return redirect('employe:employe_list')
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        form = EmployeForm()

    return render(request, 'employe/employe_form.html', {
        'form': form,
        'mode': 'ajouter',
        'champs_personnels': champs_personnels,
        'champs_professionnels': champs_professionnels
    })


def employe_update(request, pk):
    champs_personnels, champs_professionnels = get_champs_employe()
    employe = get_object_or_404(Employe, pk=pk)

    if request.method == 'POST':
        form = EmployeForm(request.POST, request.FILES, instance=employe)
        if form.is_valid():
            form.save()
            messages.success(request, "Informations employé mises à jour.")
            return redirect('employe:employe_list')
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        form = EmployeForm(instance=employe)

    return render(request, 'employe/employe_form.html', {
        'form': form,
        'mode': 'modifier',
        'employe': employe,
        'champs_personnels': champs_personnels,
        'champs_professionnels': champs_professionnels
    })

def employe_search(request):
    query = request.GET.get('q', '').strip()
    
    if query:
        employes = Employe.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(matricule__icontains=query) |
            Q(lieu_naissance__icontains=query) |
            Q(telephone__icontains=query) |
            Q(email__icontains=query) |
            Q(nationalite__icontains=query) |
            Q(statut__icontains=query) |
            Q(statut_user__icontains=query) |
            Q(grade__icontains=query) |
            Q(echelle__icontains=query) |
            Q(categorie__icontains=query)
        ).order_by('-date_creation')  # Résultats triés si recherche
    else:
        employes = Employe.objects.all().order_by('-date_creation')  # Tous les employés, triés
    paginator = Paginator(employes, 10)
    page_number = request.GET.get('page')
    employes  = paginator.get_page(page_number)
    return render(request, 'employe/employe_search.html', {
        'employes': employes,
        'query': query,
    })

# Archiver ou réactiver un employé (GET avec confirmation JavaScript)
def employe_archive(request, pk):
    employe = get_object_or_404(Employe, pk=pk)

    if employe.statut == Employe.STATUT_INACTIF:
        employe.statut = Employe.STATUT_ACTIF
        employe.save()
        messages.success(request, f"Employé {employe.matricule} réactivé avec succès.")
    else:
        employe.statut = Employe.STATUT_INACTIF
        employe.save()
        messages.success(request, f"Employé {employe.matricule} archivé avec succès.")

    return redirect('employe:employe_list')

def employe_archive_group(request):
    if request.method == 'POST':
        matricules = request.POST.getlist('matricules')
        employes = Employe.objects.filter(matricule__in=matricules)
        
        count_activés = 0
        count_archivés = 0
        
        for emp in employes:
            if emp.statut == Employe.STATUT_ACTIF:
                emp.statut = Employe.STATUT_INACTIF
                count_archivés += 1
            else:
                emp.statut = Employe.STATUT_ACTIF
                count_activés += 1
            emp.save()
        
        messages.success(request, f"{count_archivés} employé(s) archivé(s), {count_activés} employé(s) réactivé(s).")
    
    return redirect('employe:employe_list')

