# vew_print.py (app tuteur)

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image,
    Frame, PageTemplate, PageBreak
)
from django.db import models
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from datetime import datetime
from PyPDF2 import PdfMerger, PdfReader
from io import BytesIO
import os

from Gestion_adherent.Inscription_adherent.adherent.models import Adherent
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
                if i == 0 and structure:  # Vérifie que structure existe
                    generer_entete_structure_pdf(self, structure)
                if i == len(self._saved_page_states) - 1:
                    generer_pied_structure_pdf(self)
                canvas.Canvas.showPage(self)
            canvas.Canvas.save(self)

    doc.build(elements, canvasmaker=CustomCanvas)

    return response


# ---------------------- Impression liste des tuteurs ----------------------
def tuteur_print_list(request):
    tuteurs = Tuteur.objects.filter(statut=Tuteur.STATUT_ACTIF).order_by('last_name')
    structure = Structure.objects.first()  # peut être None
    MAX_ROWS_PER_PAGE = 20

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
        table = Table(data, colWidths=[100, 100, 60, 120, 120], repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        if i == 0:
            elements.append(Spacer(1, 100))
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
                if i == 0 and structure:  # Vérifie que structure existe
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

    # Portrait fiche principale du tuteur
    buffer_portrait = tuteur_print_detail(request, pk).content
    buffer_portrait_io = BytesIO(buffer_portrait)

    # PDF adhérents + opérations en mode PORTRAIT
    buffer_portrait_ops = BytesIO()
    doc_portrait_ops = SimpleDocTemplate(
        buffer_portrait_ops,
        pagesize=A4,  # ✅ On force le portrait partout
        leftMargin=30,
        rightMargin=30,
        topMargin=80,
        bottomMargin=80
    )

    # Récupération des éléments des adhérents liés au tuteur
    adherent_elements = generer_pdf_adhérents_tuteur(tuteur)

    if not isinstance(adherent_elements, list):
        raise TypeError("Les fonctions doivent retourner une liste de Flowables")

    elements = adherent_elements
    elements.append(Spacer(1, 30))

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
                if i == 0 and structure:  # Vérifie que structure existe
                    generer_entete_structure_pdf(self, structure)
                if i == len(self._saved_page_states) - 1:
                    generer_pied_structure_pdf(self)
                canvas.Canvas.showPage(self)
            canvas.Canvas.save(self)

    # Construction du PDF portrait pour les adhérents + opérations
    doc_portrait_ops.build(elements,canvasmaker=CustomCanvas)
    buffer_portrait_ops.seek(0)

    # Fusion finale des deux parties
    final_output = BytesIO()
    merger = PdfMerger()
    merger.append(PdfReader(buffer_portrait_io))
    merger.append(PdfReader(buffer_portrait_ops))
    merger.write(final_output)
    merger.close()
    final_output.seek(0)

    # Réponse HTTP avec le PDF final
    response = HttpResponse(final_output.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="operation_tuteur_{tuteur.id}.pdf"'
    return response


# ---------------------- Impression fiche + opérations ----------------------
def generer_pdf_adhérents_tuteur(tuteur):
    # Récupérer tous les adhérents pour ce tuteur (père ou mère)
    adherents = Adherent.objects.filter(models.Q(pere=tuteur) | models.Q(mere=tuteur))

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Title', parent=styles['Title'], fontName='Times-Bold', fontSize=16)
    cell_style = ParagraphStyle(name='Cell', fontName='Times-Roman', fontSize=10)

    elements = []

    # ✅ Si aucun adhérent -> on retourne une liste vide
    if not adherents.exists():
        return elements  # <--- Changement ici, plus de message PDF inutile

    # Titre
    elements.append(Paragraph(
        f"Liste des adhérents pour le tuteur : {tuteur.last_name} {tuteur.first_name}",
        title_style
    ))
    elements.append(Spacer(1, 12))

    # Préparer l'en-tête du tableau
    data = [[
        "Nom",
        "Prénom",
        "Date de naissance",
        "Lieu de naissance",
        "Sexe",
        "Téléphone",
        "Adresse",
        "Profession"
    ]]

    # Ajouter les lignes du tableau
    for a in adherents:
        data.append([
            a.last_name or "",
            a.first_name or "",
            a.date_naissance.strftime("%d/%m/%Y") if a.date_naissance else "",
            a.lieu_naissance or "",
            a.sexe or "",
            a.telephone or "",
            a.adresse or "",
            a.profession or ""
        ])

    # Création du tableau
    table = Table(data, repeatRows=1, colWidths=[80] * 8)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)
    return elements
