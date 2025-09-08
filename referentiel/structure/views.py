from django.shortcuts import render, get_object_or_404, redirect
from .models import Structure
from .forms import StructureForm
from django.db.models import Q


# 1. Consulter
def structure_list(request):
    query = request.GET.get('q', '')  # récupère la valeur de recherche

    if query:
        structures = Structure.objects.filter(
            Q(raison_sociale__icontains=query) |
            Q(email__icontains=query) |
            Q(telephone__icontains=query) |
            Q(structure_sous_tutelle__icontains=query) |
            Q(matricule__icontains=query) |
            Q(contact_personne__icontains=query) |
            Q(numero_enregistrement__icontains=query) |
            Q(site_web__icontains=query)
        ).order_by('raison_sociale')
    else:
        structures = Structure.objects.all().order_by('raison_sociale')

    return render(request, 'structure/structure_list.html', {'structures': structures})

# 2. Enregistrer
def structure_create(request):
    if request.method == 'POST':
        form = StructureForm(request.POST, request.FILES)  # <-- ajout request.FILES
        if form.is_valid():
            form.save()
            if request.POST.get("action") == "save_and_new":
                return redirect('structure:ajouter')
            return redirect('structure:liste')
    else:
        form = StructureForm()
    return render(request, 'structure/structure_form.html', {'form': form, 'mode': 'ajouter'})

# 3. Modifier
def structure_update(request, pk):
    structure = get_object_or_404(Structure, pk=pk)
    if request.method == 'POST':
        form = StructureForm(request.POST, request.FILES, instance=structure)  # <-- ici aussi
        if form.is_valid():
            form.save()
            return redirect('structure:liste')
    else:
        form = StructureForm(instance=structure)
    return render(request, 'structure/structure_form.html', {'form': form, 'mode': 'modifier'})

# 4. Rechercher
def structure_search(request):
    query = request.GET.get('q', '')  # valeur vide si pas de q dans GET
    if query:
        structures = Structure.objects.filter(
            Q(raison_sociale__icontains=query) |
            Q(email__icontains=query) |
            Q(telephone__icontains=query) |
            Q(structure_sous_tutelle__icontains=query) |
            Q(matricule__icontains=query) |
            Q(contact_personne__icontains=query) |
            Q(numero_enregistrement__icontains=query) |
            Q(site_web__icontains=query)
        ).order_by('raison_sociale')
    else:
        structures = Structure.objects.all().order_by('-date_creation')
    return render(request, 'structure/structure_search.html', {'structures': structures, 'query': query})

