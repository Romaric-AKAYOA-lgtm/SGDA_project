from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Case, When, Value, IntegerField
from django.http import HttpResponse, Http404
from datetime import datetime

from xhtml2pdf import pisa
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit

from Gestion_personnel.operation.vew_print import generer_pied_structure_pdf
from referentiel.structure.models import Structure
from referentiel.structure.vew_impression import generer_entete_structure_pdf

from .models import Operation
from .forms import OperationForm


def operation_list(request):
    query = request.GET.get('q', '').strip()

    # Récupérer uniquement les opérations dont le statut est 'confirme'
    operations_qs = Operation.objects.select_related(
        'id_employe', 'id_fonction'
    ).filter(statut='confirme')

    if query:
        filters = (
            Q(numero_fiche__icontains=query) |
            Q(numero_note__icontains=query) |
            Q(type_operation__icontains=query) |
            Q(id_employe__matricule__icontains=query) |
            Q(id_employe__last_name__icontains=query) |
            Q(id_employe__first_name__icontains=query) |
            Q(id_fonction__designation__icontains=query)
        )

        # Essayer de convertir la requête en date au format JJ/MM/AAAA
        try:
            search_date = datetime.strptime(query, "%d/%m/%Y").date()
        except ValueError:
            search_date = None

        if search_date:
            filters |= (
                Q(date_creation__date=search_date) |
                Q(date_debut__date=search_date) |
                Q(date_fin__date=search_date)
            )

        operations_qs = operations_qs.filter(filters)

    # Trier par date_creation décroissante
    operations_qs = operations_qs.order_by('-date_creation')

    paginator = Paginator(operations_qs, 10)
    page_number = request.GET.get('page')
    operations = paginator.get_page(page_number)

    return render(request, 'operation/operation_list.html', {
        'operations': operations,
        'search_query': query,
    })

# views.py
def operation_create(request):
    return handle_operation_form(request, mode='ajouter')


def operation_update(request, pk):
    operation = get_object_or_404(Operation, pk=pk)
    return handle_operation_form(request, mode='modifier', instance=operation)


def handle_operation_form(request, mode, instance=None):
    """Gestion centralisée des formulaires pour création et modification."""
    form = OperationForm(request.POST or None, instance=instance, request=request)

    if request.method == 'POST':
        if form.is_valid():
            try:
                operation = form.save(commit=False)
                # Ici on peut ajouter une logique spécifique avant la sauvegarde
                operation.save()
                form.save_m2m()  # si tu as des ManyToMany

                if mode == 'ajouter':
                    messages.success(request, "Opération enregistrée avec succès.")
                    if request.POST.get("action") == "save_and_new":
                        return redirect('operation:ajouter')
                else:
                    messages.success(request, "Opération mise à jour avec succès.")

                return redirect('operation:liste')

            except Exception as e:
                messages.error(request, f"Erreur lors de l'enregistrement : {e}")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")

    return render(request, 'operation/operation_form.html', {
        'form': form,
        'mode': mode,
        'operation': instance,
    })


def operation_search(request):
    query = request.GET.get('q', '').strip()

    operations_qs = Operation.objects.all().order_by('-date_creation')

    if query:
        filters = (
            Q(numero_fiche__icontains=query) |
            Q(numero_note__icontains=query) |
            Q(type_operation__icontains=query) |
            Q(id_employe__matricule__icontains=query) |
            Q(id_employe__last_name__icontains=query) |
            Q(id_employe__first_name__icontains=query) |
            Q(id_fonction__designation__icontains=query)
        )

        # Essayer de convertir la recherche en date au format JJ/MM/AAAA
        try:
            search_date = datetime.strptime(query, "%d/%m/%Y").date()
        except ValueError:
            search_date = None

        if search_date:
            filters |= (
                Q(date_creation__date=search_date) |
                Q(date_debut__date=search_date) |
                Q(date_fin__date=search_date)
            )

        operations_qs = operations_qs.filter(filters)

    # Annoter pour mettre les opérations 'confirme' en premier
    operations_qs = operations_qs.annotate(
        statut_priority=Case(
            When(statut='confirme', then=Value(0)),
            default=Value(1),
            output_field=IntegerField()
        )
    ).order_by('statut_priority', '-date_creation')

    # Pagination
    paginator = Paginator(operations_qs, 10)
    page_number = request.GET.get('page')
    operations = paginator.get_page(page_number)

    return render(request, 'operation/operation_search.html', {
        'operations': operations,
        'query': query,
    })


def generer_paragraphe_operation(id_operation):
    operation = get_object_or_404(Operation, id=id_operation)

    employe = operation.id_employe
    fonction = operation.id_fonction.designation
    unite = getattr(operation.id_organisation_unite, 'nom', str(operation.id_organisation_unite))
    date_debut = operation.date_debut.strftime("%d/%m/%Y")

    if operation.type_operation == 'recrutement':
        return (
            f"Par la présente, {employe.first_name} {employe.last_name} est recruté(e) en qualité de "
            f"{fonction} au sein de l’unité {unite}, à compter du {date_debut}."
        )
    elif operation.type_operation == 'mutation':
        return (
            f"{employe.first_name} {employe.last_name}, précédemment en fonction, est muté(e) en qualité de "
            f"{fonction} dans l’unité {unite}, à compter du {date_debut}."
        )
    return "Type d'opération non reconnu."


def generer_pdf_operation(request, id_operation, type_doc=None):
    """
    Génère un PDF contenant un paragraphe descriptif de l'opération.
    Le type_doc permet d'identifier le type de document à générer (certificat, attestation, etc.).
    """
    # ✅ Récupération de l'opération
    try:
        operation = Operation.objects.select_related(
            'id_employe',
            'id_fonction',
            'id_organisation_unite'
        ).get(id=id_operation)
    except Operation.DoesNotExist:
        raise Http404("Opération non trouvée.")

    # ✅ Données utilisées pour construire le paragraphe
    employe = operation.id_employe
    fonction = operation.id_fonction.designation
    unite = getattr(operation.id_organisation_unite, 'nom', str(operation.id_organisation_unite))
    date_debut = operation.date_debut.strftime("%d/%m/%Y")

    # ✅ Paragraphe personnalisé selon type_doc
    if type_doc == 'certificat':
        paragraphe = (
            f"Nous certifions que {employe.first_name} {employe.last_name} a pris service "
            f"en qualité de {fonction} au sein de l’unité {unite} depuis le {date_debut}."
        )
    elif type_doc == 'attestation_prise':
        paragraphe = (
            f"Attestation que {employe.first_name} {employe.last_name} occupe le poste de {fonction} "
            f"dans l’unité {unite} depuis le {date_debut}."
        )
    elif type_doc == 'presence':
        paragraphe = (
            f"Attestation de présence : {employe.first_name} {employe.last_name} est régulièrement présent(e) "
            f"à son poste de {fonction} au sein de l’unité {unite} depuis le {date_debut}."
        )
    elif type_doc == 'employeur':
        paragraphe = (
            f"L’employé(e) {employe.first_name} {employe.last_name} travaille comme {fonction} "
            f"dans l’unité {unite} depuis le {date_debut}."
        )
    elif type_doc == 'cessation':
        paragraphe = (
            f"Nous attestons que {employe.first_name} {employe.last_name} a cessé ses fonctions en qualité de "
            f"{fonction} dans l’unité {unite} à la date du {operation.date_fin.strftime('%d/%m/%Y') if operation.date_fin else 'non précisée'}."
        )
    else:
        # fallback classique
        if operation.type_operation == 'recrutement':
            paragraphe = (
                f"Par la présente, {employe.first_name} {employe.last_name} est recruté(e) en qualité de "
                f"{fonction} au sein de l’unité {unite}, à compter du {date_debut}."
            )
        elif operation.type_operation == 'mutation':
            paragraphe = (
                f"{employe.first_name} {employe.last_name}, précédemment en fonction, est muté(e) en qualité de "
                f"{fonction} dans l’unité {unite}, à compter du {date_debut}."
            )
        else:
            paragraphe = "Type d'opération non reconnu."

    # ✅ Préparer la réponse PDF
    filename = type_doc if type_doc else 'operation'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}.pdf"'

    # ✅ Créer le PDF
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # ✅ Position de départ
    x = 50
    y = height - 200

    # ✅ Écriture du texte (découpage auto si trop long)
    p.setFont("Times-Roman", 12)
    lines = simpleSplit(paragraphe, "Times-Roman", 12, width - 100)
    for line in lines:
        p.drawString(x, y, line)
        y -= 20

    # ✅ Finaliser le PDF
    p.showPage()
    p.save()

    return response


def generer_pdf_operation(request, id_operation):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="operation_{id_operation}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Récupère l'objet structure (exemple : la première ou celle liée à l'opération)
    structure = Structure.objects.first()  # ou adapte selon ta logique

    # Passe l'objet structure à ta fonction
    y = generer_entete_structure_pdf(p, structure)  # y reçoit la position pour continuer

    y -= 20

    paragraphe = generer_paragraphe_operation(id_operation)

    p.setFont("Times-Roman", 12)
    lines = simpleSplit(paragraphe, "Times-Roman", 12, width - 100)
    for line in lines:
        if y < 100:
            p.showPage()
            p.setFont("Times-Roman", 12)
            y = height - 100
        p.drawString(50, y, line)
        y -= 20

    generer_pied_structure_pdf(p,)

    p.showPage()
    p.save()

    return response

