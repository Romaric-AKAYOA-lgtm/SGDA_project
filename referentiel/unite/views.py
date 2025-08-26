from django.shortcuts import render, get_object_or_404, redirect
from .models import Unite
from .forms import UniteForm
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import render_to_string


# 1. Consulter
def unite_list(request):
    query = request.GET.get('q', '')  # récupère la valeur de recherche

    if query:
        unites = Unite.objects.filter(designation__icontains=query)
    else:
        unites = Unite.objects.all().order_by('unite_parent')

    return render(request, 'unite/unite_list.html', {'unites': unites})

# 2. Enregistrer
def unite_create(request):
    if request.method == 'POST':
        form = UniteForm(request.POST)
        if form.is_valid():
            form.save()
            if request.POST.get("action") == "save_and_new":
                return redirect('unite:ajouter')  # rester sur le formulaire vide
            return redirect('unite:liste')
    else:
        form = UniteForm()
    return render(request, 'unite/unite_form.html', {'form': form, 'mode': 'ajouter'})

# 3. Modifier
def unite_update(request, pk):
    unite = get_object_or_404(Unite, pk=pk)
    if request.method == 'POST':
        form = UniteForm(request.POST, instance=unite)
        if form.is_valid():
            form.save()
            return redirect('unite:liste')  # idem ici
    else:
        form = UniteForm(instance=unite)
    return render(request, 'unite/unite_form.html', {'form': form, 'mode': 'modifier'})

# 4. Rechercher
def unite_search(request):
    query = request.GET.get('q', '')  # valeur vide si pas de q dans GET
    if query:
        unites = Unite.objects.filter(Q(designation__icontains=query))
    else:
        unites = Unite.objects.all().order_by('unite_parent')
    return render(request, 'unite/unite_search.html', {'unites': unites, 'query': query})
