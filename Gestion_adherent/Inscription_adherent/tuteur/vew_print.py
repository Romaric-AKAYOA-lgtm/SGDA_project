# vew_print.py (app tuteur)

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image,
    Frame, PageTemplate, PageBreak
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from datetime import datetime
from PyPDF2 import PdfMerger, PdfReader
from io import BytesIO
import os

from Gestion_personnel.absence.vew_print import generer_pdf_absences_employe as generer_pdf_absences_tuteur
from Gestion_personnel.operation.models import Operation
from Gestion_personnel.operation.vew_print import generer_pdf_operations_employe as generer_pdf_operations_tuteur
from Gestion_personnel.operation.views import generer_pied_structure_pdf
from referentiel.structure.models import Structure
from referentiel.structure.vew_impression import generer_entete_structure_pdf
from .models import Tuteur


# ---------------------- Impression fiche individuelle ----------------------
def tuteur_print_detail(request, pk):
    tuteur = get_object_or_404(Tuteur, pk=pk)
    structure = Structure.objects.first()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="fiche_tuteur_{tuteur.id}.pdf"'

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
    title = Paragraph(f"Fiche Tuteur : {tuteur.last_name} {tuteur.first_name}", title_style)
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
        [Paragraph("Nom", cell_style), Paragraph(tuteur.last_name or '', cell_style)],
        [Paragraph("Prénom", cell_style), Paragraph(tuteur.first_name or '', cell_style)],
        [Paragraph("Date de naissance", cell_style), Paragraph(tuteur.date_naissance.strftime('%d/%m/%Y') if tuteur.date_naissance else '', cell_style)],
        [Paragraph("Lieu de naissance", cell_style), Paragraph(tuteur.lieu_naissance or '', cell_style)],
        [Paragraph("Sexe", cell_style), Paragraph(tuteur.get_sexe_display() if hasattr(tuteur, 'get_sexe_display') else tuteur.sexe or '', cell_style)],
        [Paragraph("Téléphone", cell_style), Paragraph(tuteur.telephone or '', cell_style)],
        [Paragraph("Nationalité", cell_style), Paragraph(tuteur.nationalite or '', cell_style)],
        [Paragraph("Adresse", cell_style), Paragraph(tuteur.adresse or '', cell_style)],
        [Paragraph("Statut utilisateur", cell_style), Paragraph(tuteur.statut_user or '', cell_style)],
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
        generer_pied_structure_pdf(pdf_canvas)

    doc.build(elements, onFirstPage=lambda c, d: (en_tete_page(c, d), pied_de_page(c, d)))

    return response


# ---------------------- Impression liste des tuteurs ----------------------
def tuteur_print_list(request):
    tuteurs = Tuteur.objects.filter(statut=Tuteur.STATUT_ACTIF).order_by('last_name')
    structure = Structure.objects.first()
    MAX_ROWS_PER_PAGE = 15

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontName='Times-Bold', fontSize=20, alignment=1, spaceAfter=20)
    header_style = ParagraphStyle('Header', fontName='Times-Bold', fontSize=10, alignment=1)
    cell_style = ParagraphStyle('Cell', fontName='Times-Roman', fontSize=9)

    headers = ["Nom", "Prénom", "Sexe", "Téléphone", "Email"]

    all_rows = []
    for tut in tuteurs:
        all_rows.append([
            Paragraph(tut.last_name or '', cell_style),
            Paragraph(tut.first_name or '', cell_style),
            Paragraph(tut.get_sexe_display() if hasattr(tut, 'get_sexe_display') else '', cell_style),
            Paragraph(tut.telephone or '', cell_style),
            Paragraph(tut.email or '', cell_style),
        ])

    elements = [Spacer(1, 30)]
    for i, start in enumerate(range(0, len(all_rows), MAX_ROWS_PER_PAGE)):
        chunk = all_rows[start:start + MAX_ROWS_PER_PAGE]
        data = [[Paragraph(h, header_style) for h in headers]] + chunk
        table = Table(data, colWidths=[100, 100, 40, 100, 120], repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        if i == 0:
            elements.append(Paragraph("<u>Liste des Tuteurs</u>", title_style))
            elements.append(Spacer(1, 20))

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
                if i == 0:
                    generer_entete_structure_pdf(self, structure)
                if i == len(self._saved_page_states) - 1:
                    generer_pied_structure_pdf(self)
                canvas.Canvas.showPage(self)
            canvas.Canvas.save(self)

    doc.build(elements, canvasmaker=CustomCanvas)

    response = HttpResponse(final_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="liste_tuteurs.pdf"'
    return response


# ---------------------- Impression fiche + opérations ----------------------
def tuteur_print_list_operation(request, pk):
    tuteur = get_object_or_404(Tuteur, pk=pk)
    structure = Structure.objects.first()

    # Portrait fiche
    buffer_portrait = tuteur_print_detail(request, pk).content
    buffer_portrait_io = BytesIO(buffer_portrait)

    # Paysage opérations + absences
    buffer_landscape = BytesIO()
    doc_landscape = SimpleDocTemplate(buffer_landscape, pagesize=landscape(A4), leftMargin=30, rightMargin=30, topMargin=80, bottomMargin=80)

    ops_elements = generer_pdf_operations_tuteur(tuteur)
    abs_elements = generer_pdf_absences_tuteur(tuteur)

    if not isinstance(ops_elements, list) or not isinstance(abs_elements, list):
        raise TypeError("Les fonctions doivent retourner une liste de Flowables")

    elements = ops_elements + abs_elements
    elements.append(Spacer(1, 30))

    def en_tete_page(pdf_canvas, doc):
        if structure:
            generer_entete_structure_pdf(pdf_canvas, structure)

    def pied_de_page(pdf_canvas, doc):
        generer_pied_structure_pdf(pdf_canvas)

    doc_landscape.build(elements, onFirstPage=lambda c, d: (en_tete_page(c, d), pied_de_page(c, d)), onLaterPages=lambda c, d: pied_de_page(c, d))

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
    response['Content-Disposition'] = f'inline; filename="operation_tuteur_{tuteur.id}.pdf"'
    return response
