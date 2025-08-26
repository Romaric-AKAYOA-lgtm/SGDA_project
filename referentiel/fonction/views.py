from django.shortcuts import render, get_object_or_404, redirect
from .models import Fonction
from .forms import FonctionForm
from django.db.models import Q

# 1. Consulter
def fonction_list(request):
    query = request.GET.get('q', '')  # récupère la valeur de recherche

    if query:
        fonctions = Fonction.objects.filter(designation__icontains=query)
    else:
        fonctions = Fonction.objects.all().order_by('fonction_parent')

    return render(request, 'fonction/fonction_list.html', {'fonctions': fonctions})

# 2. Enregistrer
def fonction_create(request):
    if request.method == 'POST':
        form = FonctionForm(request.POST)
        if form.is_valid():
            form.save()
            if request.POST.get("action") == "save_and_new":
                return redirect('fonction:ajouter')  # rester sur le formulaire vide
            return redirect('fonction:liste')
    else:
        form = FonctionForm()
    return render(request, 'fonction/fonction_form.html', {'form': form, 'mode': 'ajouter'})

# 3. Modifier
def fonction_update(request, pk):
    fonction = get_object_or_404(Fonction, pk=pk)
    if request.method == 'POST':
        form = FonctionForm(request.POST, instance=fonction)
        if form.is_valid():
            form.save()
            return redirect('fonction:liste')
    else:
        form = FonctionForm(instance=fonction)
    return render(request, 'fonction/fonction_form.html', {'form': form, 'mode': 'modifier'})

# 4. Rechercher
def fonction_search(request):
    query = request.GET.get('q', '')  # valeur vide si pas de q dans GET
    if query:
        fonctions = Fonction.objects.filter(Q(designation__icontains=query))
    else:
        fonctions = Fonction.objects.all().order_by('fonction_parent')
    return render(request, 'fonction/fonction_search.html', {'fonctions': fonctions, 'query': query})

