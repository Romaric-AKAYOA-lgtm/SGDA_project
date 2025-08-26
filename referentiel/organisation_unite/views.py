from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from .models import OrganisationUnite
from .forms import OrganisationUniteForm
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import render_to_string

# 1. Consulter
def organisation_unite_list(request):
    query = request.GET.get('q', '')
    if query:
        organisations = OrganisationUnite.objects.filter(
            Q(designation__icontains=query) |
            Q(unite__designation__icontains=query) |
            Q(structure__raison_sociale__icontains=query) |
            Q(organisation_unite_parent__designation__icontains=query)
        )
    else:
        organisations = OrganisationUnite.objects.all().order_by('-date_creation')

    return render(request, 'organisation_unite/organisation_unite_list.html', {
        'organisations': organisations
    })

# 2. Enregistrer
def organisation_unite_create(request):
    if request.method == 'POST':
        form = OrganisationUniteForm(request.POST)
        if form.is_valid():
            form.save()
            if request.POST.get("action") == "save_and_new":
                return redirect('organisation_unite:ajouter')
            return redirect('organisation_unite:liste')
    else:
        form = OrganisationUniteForm()

    return render(request, 'organisation_unite/organisation_unite_form.html', {
        'form': form,
        'mode': 'ajouter'
    })

# 3. Modifier
def organisation_unite_update(request, pk):
    organisation = get_object_or_404(OrganisationUnite, pk=pk)
    if request.method == 'POST':
        form = OrganisationUniteForm(request.POST, instance=organisation)
        if form.is_valid():
            form.save()
            return redirect('organisation_unite:liste')
    else:
        form = OrganisationUniteForm(instance=organisation)

    return render(request, 'organisation_unite/organisation_unite_form.html', {
        'form': form,
        'mode': 'modifier'
    })

# 4. Rechercher
def organisation_unite_search(request):
    query = request.GET.get('q', '')
    if query:
                organisations = OrganisationUnite.objects.filter(
                Q(designation__icontains=query) |
                Q(unite__designation__icontains=query) |
                Q(structure__raison_sociale__icontains=query) |
                Q(organisation_unite_parent__designation__icontains=query)
            )
    else:
        organisations = OrganisationUnite.objects.all().order_by("-date_creation")

    return render(request, 'organisation_unite/organisation_unite_search.html', {
        'organisations': organisations,
        'query': query
    })
