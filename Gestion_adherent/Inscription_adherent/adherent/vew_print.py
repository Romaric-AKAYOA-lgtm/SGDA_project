# vew_print.py (app adherent)
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak
)

from PyPDF2 import PdfMerger, PdfReader
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

from referentiel.structure.models import Structure
from referentiel.structure.vew_impression import generer_entete_structure_pdf
from Gestion_personnel.operation.vew_print import generer_pdf_operations_employe
from Gestion_personnel.absence.vew_print import generer_pdf_absences_employe
from .models import Adherent


# ---------------------- Impression fiche individuelle ----------------------
def adherent_print_detail(request, pk):
    adherent = get_object_or_404(Adherent, pk=pk)
    structure = Structure.objects.first()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="fiche_adherent_{adherent.id}.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        topMargin=280,
        leftMargin=50,
        rightMargin=50,
        bottomMargin=50,
    )

    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name='TitleTimes',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=18,
        leading=22,
    )
    elements.append(Spacer(1, 20))
    title = Paragraph(f"Fiche Adhérent : {adherent.last_name} {adherent.first_name}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 20))

    cell_style = ParagraphStyle(
        name='CellStyleTimes',
        fontName='Times-Roman',
        fontSize=12,
        leading=14,
    )
    data = [
        [Paragraph("Champ", title_style), Paragraph("Valeur", title_style)],
        [Paragraph("Nom", cell_style), Paragraph(adherent.last_name or '', cell_style)],
        [Paragraph("Prénom", cell_style), Paragraph(adherent.first_name or '', cell_style)],
        [Paragraph("Date de naissance", cell_style), Paragraph(adherent.date_naissance.strftime('%d/%m/%Y') if adherent.date_naissance else '', cell_style)],
        [Paragraph("Lieu de naissance", cell_style), Paragraph(adherent.lieu_naissance or '', cell_style)],
        [Paragraph("Téléphone", cell_style), Paragraph(adherent.telephone or '', cell_style)],
        [Paragraph("Email", cell_style), Paragraph(adherent.email or '', cell_style)],
        [Paragraph("Adresse", cell_style), Paragraph(adherent.adresse or '', cell_style)],
        [Paragraph("Statut utilisateur", cell_style), Paragraph(adherent.statut_user or '', cell_style)],
        [Paragraph("Père", cell_style), Paragraph(f"{adherent.pere.nom} {adherent.pere.prenom}" if adherent.pere else '', cell_style)],
        [Paragraph("Mère", cell_style), Paragraph(f"{adherent.mere.nom} {adherent.mere.prenom}" if adherent.mere else '', cell_style)],
    ]

    table = Table(data, colWidths=[150, 300], splitByRow=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table)

    def en_tete_page(pdf_canvas, doc):
        if structure:
            generer_entete_structure_pdf(pdf_canvas, structure)

    def pied_de_page(pdf_canvas, doc):
        pass  # à compléter si tu as un pied de page spécifique

    doc.build(elements, onFirstPage=lambda c, d: (en_tete_page(c, d), pied_de_page(c, d)))

    return response


# ---------------------- Impression liste des adhérents ----------------------
def adherent_print_list(request):
    adherents = Adherent.objects.filter(statut=Adherent.STATUT_ACTIF).order_by('last_name')
    structure = Structure.objects.first()
    MAX_ROWS_PER_PAGE = 15

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontName='Times-Bold', fontSize=20, alignment=1, spaceAfter=20)
    header_style = ParagraphStyle('Header', fontName='Times-Bold', fontSize=10, alignment=1)
    cell_style = ParagraphStyle('Cell', fontName='Times-Roman', fontSize=9)

    headers = ["Nom", "Prénom", "Téléphone", "Email"]

    all_rows = []
    for ad in adherents:
        all_rows.append([
            Paragraph(ad.last_name or '', cell_style),
            Paragraph(ad.first_name or '', cell_style),
            Paragraph(ad.telephone or '', cell_style),
            Paragraph(ad.email or '', cell_style),
        ])

    elements = [Spacer(1, 30)]
    for i, start in enumerate(range(0, len(all_rows), MAX_ROWS_PER_PAGE)):
        chunk = all_rows[start:start + MAX_ROWS_PER_PAGE]
        data = [[Paragraph(h, header_style) for h in headers]] + chunk
        table = Table(data, colWidths=[100, 100, 100, 150], repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        if i == 0:
            elements.append(Paragraph("<u>Liste des Adhérents</u>", title_style))
            elements.append(Spacer(1, 20))
        elements.append(table)
        if start + MAX_ROWS_PER_PAGE < len(all_rows):
            elements.append(PageBreak())

    final_buffer = BytesIO()
    doc = SimpleDocTemplate(final_buffer, pagesize=A4, topMargin=180, leftMargin=50, rightMargin=50, bottomMargin=80)
    doc.build(elements)

    response = HttpResponse(final_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="liste_adherents.pdf"'
    return response


# ---------------------- Impression fiche + opérations ----------------------
def adherent_print_list_operation(request, pk):
    adherent = get_object_or_404(Adherent, pk=pk)
    structure = Structure.objects.first()

    # Portrait fiche
    buffer_portrait = adherent_print_detail(request, pk).content
    buffer_portrait_io = BytesIO(buffer_portrait)

    # Paysage opérations + absences
    buffer_landscape = BytesIO()
    doc_landscape = SimpleDocTemplate(buffer_landscape, pagesize=landscape(A4), leftMargin=30, rightMargin=30, topMargin=80, bottomMargin=80)

    ops_elements = generer_pdf_operations_employe(adherent)
    abs_elements = generer_pdf_absences_employe(adherent)

    if not isinstance(ops_elements, list) or not isinstance(abs_elements, list):
        raise TypeError("Les fonctions doivent retourner une liste de Flowables")

    elements = ops_elements + abs_elements
    elements.append(Spacer(1, 30))

    def en_tete_page(pdf_canvas, doc):
        if structure:
            generer_entete_structure_pdf(pdf_canvas, structure)

    def pied_de_page(pdf_canvas, doc):
        pass

    doc_landscape.build(elements, onFirstPage=lambda c, d: (en_tete_page(c, d), pied_de_page(c, d)),
                        onLaterPages=lambda c, d: pied_de_page(c, d))
    buffer_landscape.seek(0)

    # Fusion
    final_output = BytesIO()
    merger = PdfMerger()
    merger.append(PdfReader(buffer_portrait_io))
    merger.append(PdfReader(buffer_landscape))
    merger.write(final_output)
    merger.close()
    final_output.seek(0)

    response = HttpResponse(final_output.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="operation_adherent_{adherent.id}.pdf"'
    return response
