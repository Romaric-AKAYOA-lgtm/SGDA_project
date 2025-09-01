from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from Gestion_personnel.operation.vew_print1 import generer_pied_structure_pdf
from referentiel.structure.vew_impression import generer_entete_structure_pdf
from .models import Cotisation
from .forms import CotisationForm
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
    cotisations = Cotisation.objects.all().order_by('-date_cotisation')
    structure = Structure.objects.first()  # peut être None
    MAX_ROWS_PER_PAGE = 20

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontName='Times-Bold', fontSize=20, alignment=1, spaceAfter=20)
    header_style = ParagraphStyle('Header', fontName='Times-Bold', fontSize=10, alignment=1)
    cell_style = ParagraphStyle('Cell', fontName='Times-Roman', fontSize=9)

    headers = ["Adhérent", "Montant", "Date cotisation", "Statut"]

    all_rows = []
    for cot in cotisations:
        all_rows.append([
            Paragraph(f"{cot.adherent.last_name} {cot.adherent.first_name}", cell_style),
            Paragraph(str(cot.montant)+" FCFA" if cot.montant else '', cell_style),
            Paragraph(cot.date_cotisation.strftime('%d/%m/%Y') if cot.date_cotisation else '', cell_style),
            Paragraph(cot.statut or '', cell_style),
        ])

    elements = [Spacer(1, 30)]
    for i, start in enumerate(range(0, len(all_rows), MAX_ROWS_PER_PAGE)):
        chunk = all_rows[start:start + MAX_ROWS_PER_PAGE]
        data = [[Paragraph(h, header_style) for h in headers]] + chunk
        table = Table(data, colWidths=[150, 80, 100, 120], repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        if i == 0:
            elements.append(Spacer(1, 90))
            elements.append(Paragraph("<u>Liste des Cotisations</u>", title_style))
            elements.append(Spacer(1, 15))

        elements.append(table)

        if start + MAX_ROWS_PER_PAGE < len(all_rows):
            elements.append(PageBreak())

    final_buffer = BytesIO()
    doc = SimpleDocTemplate(final_buffer, pagesize=A4, topMargin=180, leftMargin=50, rightMargin=50, bottomMargin=80)

    class CustomCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            for i, state in enumerate(self._saved_page_states):
                self.__dict__.update(state)
                if i == 0 and structure:
                    generer_entete_structure_pdf(self, structure)
                if i == len(self._saved_page_states) - 1:
                    generer_pied_structure_pdf(self)
                canvas.Canvas.showPage(self)
            canvas.Canvas.save(self)

    doc.build(elements, canvasmaker=CustomCanvas)

    response = HttpResponse(final_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="liste_cotisations.pdf"'
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

    # === Génération du PDF ===
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cotisation_{pk}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, topMargin=180, leftMargin=50, rightMargin=50, bottomMargin=80)
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontName='Times-Bold', fontSize=18, leading=22)
    cell_style = ParagraphStyle('Cell', fontName='Times-Roman', fontSize=12, leading=14)

    # Titre
    elements.append(Spacer(1, 120))
    elements.append(Paragraph("Détails des Cotisations", title_style))
    elements.append(Spacer(1, 20))

    # Préparer les données du tableau
    data = [[Paragraph("Adhérent", title_style),
             Paragraph("Montant", title_style),
             Paragraph("Date de cotisation", title_style),
             Paragraph("Mode de paiement", title_style),
           ]]

    # Remplir le tableau avec les cotisations trouvées
    for c in cotisations:
        data.append([
            Paragraph(f"{c.adherent.last_name} {c.adherent.first_name}", cell_style),
            Paragraph(str(c.montant)+" FCFA" if c.montant else "", cell_style),
            Paragraph(c.date_cotisation.strftime('%d/%m/%Y') if c.date_cotisation else "", cell_style),
            Paragraph(c.statut or "", cell_style),
        ])

    # Créer le tableau
    # Largeur totale A4 ≈ 595, marges gauche/droite 50 => largeur utile ≈ 495
    # Largeur utile pour A4 = 595 - (marges gauche+droite)
    table = Table(
        data,
        colWidths=[180, 120, 120, 120, 120],  # Colonnes plus larges
        splitByRow=1
    )
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(table)

    # Entête & pied de page
    def en_tete_page(pdf_canvas, doc):
        if structure:
            generer_entete_structure_pdf(pdf_canvas, structure)

    def pied_de_page(pdf_canvas, doc):
        generer_pied_structure_pdf(pdf_canvas)

    # Construire le PDF
    doc.build(elements, onFirstPage=lambda c, d: (en_tete_page(c, d), pied_de_page(c, d)))

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
