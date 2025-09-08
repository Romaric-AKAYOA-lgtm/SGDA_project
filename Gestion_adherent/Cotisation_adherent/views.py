from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import Sum
from django.utils.timezone import now
from django.db.models import Sum
from Gestion_personnel.operation.vew_print1 import generer_pied_structure_pdf
from referentiel.structure.vew_impression import generer_entete_structure_pdf
from .models import Cotisation
from .forms import CotisationForm
from reportlab.pdfgen import canvas as rcanvas
from datetime import datetime, timedelta
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

from .models import Cotisation
from referentiel.structure.models import Structure  # si tu as ce modèle

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
    # On passe request au formulaire pour récupérer l'utilisateur connecté
    form = CotisationForm(request.POST or None, request=request)

    if request.method == 'POST':
        form = CotisationForm(request.POST, request=request)
        if form.is_valid():
            cotisation = form.save(commit=False)
            # Définir le statut en fonction du type et montant
            cotisation.statut = Cotisation.STATUT_VALIDE if is_cotisation_valide(cotisation) else Cotisation.STATUT_INVALIDE
            # L'opération est déjà forcée dans le clean du formulaire
            cotisation.save()
            messages.success(request, "Cotisation enregistrée avec succès.")
            if request.POST.get("action") == "save_and_new":
                return redirect('cotisation:cotisation_create')
            return redirect('cotisation:cotisation_list')
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")

    return render(request, 'Cotisation_adherent/cotisation_form.html', {
        'form': form,
        'mode': 'ajouter'
    })


# Modification d'une cotisation
def cotisation_update(request, pk):
    cotisation = get_object_or_404(Cotisation, pk=pk)

    if request.method == 'POST':
        form = CotisationForm(request.POST, instance=cotisation, request=request)
        if form.is_valid():
            cotisation = form.save(commit=False)
            # Statut basé sur la validation
            cotisation.statut = Cotisation.STATUT_VALIDE if is_cotisation_valide(cotisation) else Cotisation.STATUT_INVALIDE
            # L'opération reste forcée par le formulaire (utilisateur connecté)
            cotisation.save()
            messages.success(request, "Cotisation mise à jour avec succès.")
            return redirect('cotisation:cotisation_list')
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        form = CotisationForm(instance=cotisation, request=request)

    return render(request, 'Cotisation_adherent/cotisation_form.html', {
        'form': form,
        'mode': 'modifier',
        'cotisation': cotisation
    })


def cotisation_archive(request, pk):
    cotisation = get_object_or_404(Cotisation, pk=pk)

    if cotisation.statut == Cotisation.STATUT_INVALIDE:
        cotisation.statut = Cotisation.STATUT_VALIDE
        messages.success(request, "Cotisation réactivée avec succès.")
    else:
        cotisation.statut = Cotisation.STATUT_INVALIDE
        messages.success(request, "Cotisation archivée avec succès.")

    cotisation.save()  # on sauvegarde après modification du statut
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
                c.save()
            else:
                c.statut = Cotisation.STATUT_VALIDE
                count_valide += 1
                c.save()
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
    paginator = Paginator(cotisations, 10)
    page_number = request.GET.get('page')
    cotisations = paginator.get_page(page_number)
    return render(request, 'Cotisation_adherent/cotisation_search.html', {
        'cotisations': cotisations,
        'query': query
    })


# -----------------------------------------
# Liste des cotisations en PDF
# -----------------------------------------
def cotisation_print_list(request):
    current_year = now().year

    cotisations = Cotisation.objects.filter(date_cotisation__year=current_year).order_by('-date_cotisation')

    # Nombre total de cotisations
    cotisation_total = cotisations.count()

    # Somme totale des montants
    # Somme totale des montants
    total_montant = cotisations.aggregate(total=Sum('montant'))['total'] or 0

    # Convertir en chaîne avec unité
    cotisation_montant_total = f"{total_montant} FCFA"
    structure = Structure.objects.first()  # peut être None

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title', parent=styles['Title'], fontName='Times-Bold',
        fontSize=20, alignment=1, spaceAfter=20
    )
    header_style = ParagraphStyle(
        'Header', fontName='Times-Bold', fontSize=10, alignment=1
    )
    cell_style = ParagraphStyle(
        'Cell', fontName='Times-Roman', fontSize=9
    )

    headers = ["Adhérent","Téléphone", "Montant", "Date cotisation", "Statut"]

    # Préparer toutes les lignes du tableau
    all_rows = [] 
    for cot in cotisations:
        all_rows.append([
            Paragraph(f"{cot.adherent.last_name} {cot.adherent.first_name}", cell_style),
            Paragraph(f"{cot.adherent.telephone}", cell_style),
            Paragraph(f"{cot.montant} FCFA" if cot.montant else '', cell_style),
            Paragraph(cot.date_cotisation.strftime('%d/%m/%Y') if cot.date_cotisation else '', cell_style),
            Paragraph(cot.statut or '', cell_style),
        ])

    elements = [Spacer(1, 100)]
    elements.append(Spacer(1, 150))
    elements.append(Paragraph(f"<u>Liste des Cotisations de l\'année  {current_year}</u>", title_style))
    elements.append(Spacer(1, 10))

    # Création du tableau complet sans pagination
    data = [[Paragraph(h, header_style) for h in headers]] + all_rows 
    table = Table(data, colWidths=[150,80, 80, 60, 50], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Nombre total de cotisation : {cotisation_total}", cell_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Montant total de cotisation : {cotisation_montant_total}", cell_style))
    elements.append(Spacer(1, 10))
    # Génération PDF
    final_buffer = BytesIO()


    class CustomCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total_pages = len(self._saved_page_states)
            for i, state in enumerate(self._saved_page_states):
                self.__dict__.update(state)

                # Ajouter en-tête sur la première page
                if i == 0:
                    generer_entete_structure_pdf(self, structure)

                # Ajouter pied sur la dernière page
                if i == total_pages - 1:
                    generer_pied_structure_pdf(self)

                # Ajouter numéro de page en bas à droite
                page_num_text = f"Page {i + 1} / {total_pages}"
                self.setFont("Times-Roman", 9)
                self.drawRightString(550, 20, page_num_text)  # Position bas à droite

                super().showPage()
            super().save()
    response = HttpResponse(final_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="liste_cotisations.pdf"'
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        topMargin=50,
        leftMargin=50,
        rightMargin=50,
        bottomMargin=50,
    )
    doc.build(elements, canvasmaker=CustomCanvas)

    return response


# -----------------------------------------
# Détail d'une cotisation en PDF
# -----------------------------------------
def cotisation_print_detail(request, pk):
    structure = Structure.objects.first()

    # Vérifier si pk correspond à une cotisation
    cotisation = Cotisation.objects.filter(pk=pk).first()
    if cotisation:
        # === CAS 1 : Une seule cotisation ===
        cotisations = [cotisation]
    else:
        # === CAS 2 : pk correspond à un adherent_id ===
        cotisations = Cotisation.objects.filter(adherent_id=pk)
        if not cotisations.exists():
            return HttpResponse("Aucune cotisation trouvée pour cet adhérent ou cette cotisation.", status=404)

    # Création d'un buffer mémoire pour générer le PDF
    final_buffer = BytesIO()

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontName='Times-Bold', fontSize=18, alignment=1, spaceAfter=15)
    header_style = ParagraphStyle('Header', fontName='Times-Bold', fontSize=11, alignment=1)
    cell_style = ParagraphStyle('Cell', fontName='Times-Roman', fontSize=10, alignment=1)

    # Contenu du PDF
    elements = []
    elements.append(Spacer(1, 120))
    elements.append(Paragraph("<u>Détails des Cotisations</u>", title_style))
    elements.append(Spacer(1, 20))

    # En-têtes du tableau
    data = [[
        Paragraph("Adhérent", header_style),
        Paragraph("Montant", header_style),
        Paragraph("Date de cotisation", header_style),
        Paragraph("Statut", header_style),
    ]]

    # Remplir le tableau avec les cotisations
    for c in cotisations:
        data.append([
            Paragraph(f"{c.adherent.last_name} {c.adherent.first_name}", cell_style),
            Paragraph(f"{c.montant} FCFA" if c.montant else "", cell_style),
            Paragraph(c.date_cotisation.strftime('%d/%m/%Y') if c.date_cotisation else "", cell_style),
            Paragraph(c.statut or "", cell_style),
        ])

    # Créer le tableau
    table = Table(data, colWidths=[180, 120, 120, 120], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    elements.append(table)

    # Ajouter le nombre total
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Nombre total de cotisations : {len(cotisations)}", cell_style))
    elements.append(Spacer(1, 10))

    # === Classe personnalisée pour en-tête, pied de page et pagination ===
    class CustomCanvas(rcanvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total_pages = len(self._saved_page_states)
            for i, state in enumerate(self._saved_page_states):
                self.__dict__.update(state)

                # En-tête uniquement sur la première page
                if i == 0:
                    generer_entete_structure_pdf(self, structure)

                # Pied de page sur la dernière page
                if i == total_pages - 1:
                    generer_pied_structure_pdf(self)

                # Numéro de page en bas à droite
                page_num_text = f"Page {i + 1} / {total_pages}"
                self.setFont("Times-Roman", 9)
                self.drawRightString(550, 20, page_num_text)

                super().showPage()
            super().save()

    # Création du document PDF
    doc = SimpleDocTemplate(
        final_buffer,
        pagesize=A4,
        topMargin=50,
        leftMargin=50,
        rightMargin=50,
        bottomMargin=50,
    )
    doc.build(elements, canvasmaker=CustomCanvas)

    # Réponse HTTP
    response = HttpResponse(final_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cotisation_{pk}.pdf"'
    return response



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
