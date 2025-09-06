from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image,
    Frame,
    PageTemplate
)
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
from PyPDF2 import PdfMerger, PdfReader
from io import BytesIO
import os

# Importations des fonctions personnalisées
from Gestion_personnel.absence.vew_print import generer_pdf_absences_employe
from Gestion_personnel.operation.vew_print1 import generer_pdf_operations_employe
from Gestion_personnel.operation.views import generer_pied_structure_pdf
from referentiel.structure.models import Structure
from referentiel.structure.vew_impression import generer_entete_structure_pdf
from Gestion_personnel.employe.models import Employe

def employe_print_detail(request, pk):
    employe = get_object_or_404(Employe, pk=pk)
    structure = Structure.objects.first()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="fiche_employe_{employe.matricule}.pdf"'

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
        wordWrap='CJK',
    )
    elements.append(Spacer(1, 20))
    title = Paragraph(f"Fiche Employé : {employe.last_name} {employe.first_name}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 20))

    cell_style = ParagraphStyle(
        name='CellStyleTimes',
        fontName='Times-Roman',
        fontSize=12,
        leading=14,
        wordWrap='CJK',
    )

    data = [
        [Paragraph("Champ", title_style), Paragraph("Valeur", title_style)],
        [Paragraph("Matricule", cell_style), Paragraph(employe.matricule or '', cell_style)],
        [Paragraph("Nom", cell_style), Paragraph(employe.last_name or '', cell_style)],
        [Paragraph("Prénom", cell_style), Paragraph(employe.first_name or '', cell_style)],
        [Paragraph("Date de naissance", cell_style), Paragraph(employe.date_naissance.strftime('%d/%m/%Y') if employe.date_naissance else '', cell_style)],
        [Paragraph("Lieu de naissance", cell_style), Paragraph(employe.lieu_naissance or '', cell_style)],
        [Paragraph("Sexe", cell_style), Paragraph(employe.get_sexe_display() if hasattr(employe, 'get_sexe_display') else employe.sexe or '', cell_style)],
        [Paragraph("Téléphone", cell_style), Paragraph(employe.telephone or '', cell_style)],
        [Paragraph("Nationalité", cell_style), Paragraph(employe.nationalite or '', cell_style)],
        [Paragraph("Adresse", cell_style), Paragraph(employe.adresse or '', cell_style)],
        [Paragraph("Statut", cell_style), Paragraph(employe.get_statut_display() if hasattr(employe, 'get_statut_display') else employe.statut or '', cell_style)],
        [Paragraph("Grade", cell_style), Paragraph(employe.grade or '', cell_style)],
        [Paragraph("Echelle", cell_style), Paragraph(str(employe.echelle) if employe.echelle is not None else '', cell_style)],
        [Paragraph("Catégorie", cell_style), Paragraph(employe.categorie or '', cell_style)],
        # Ajoute d'autres champs si besoin
    ]

    table = Table(data, colWidths=[150, 300], splitByRow=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),

        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),

        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    def en_tete_page(pdf_canvas, doc):
        if structure:
            generer_entete_structure_pdf(pdf_canvas, structure)

    def pied_de_page (canvas, doc):
        generer_pied_structure_pdf(canvas)

    def on_page(pdf_canvas, doc):
        en_tete_page(pdf_canvas, doc)
        pied_de_page(pdf_canvas, doc)

    doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)

    return response


from io import BytesIO
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas as rcanvas
from io import BytesIO

def employe_print_list(request):
    employes = Employe.objects.filter(statut=Employe.STATUT_ACTIF).order_by('matricule')
    structure = Structure.objects.first()
    MAX_ROWS_PER_PAGE = 15  # Ajuste selon la taille du tableau et la page

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontName='Times-Bold', fontSize=20, alignment=1, spaceAfter=20)
    header_style = ParagraphStyle('Header', fontName='Times-Bold', fontSize=10, alignment=1)
    cell_style = ParagraphStyle('Cell', fontName='Times-Roman', fontSize=9)

    headers = ["Matricule", "Nom", "Prénom", "Sexe", "Statut", "Téléphone", "Email"]

    # Construire les lignes du tableau
    all_rows = []
    for emp in employes:
        all_rows.append([
            Paragraph(emp.matricule or '', cell_style),
            Paragraph(emp.last_name or '', cell_style),
            Paragraph(emp.first_name or '', cell_style),
            Paragraph(emp.get_sexe_display() if hasattr(emp, 'get_sexe_display') else '', cell_style),
            Paragraph(emp.get_statut_display() or '', cell_style),
            Paragraph(emp.telephone or '', cell_style),
            Paragraph(emp.email or '', cell_style),
        ])

    elements = []
    elements.append(Spacer(1, 30))
    # Découper en blocs pour chaque page
    for i, start in enumerate(range(0, len(all_rows), MAX_ROWS_PER_PAGE)):
        chunk = all_rows[start:start + MAX_ROWS_PER_PAGE]
        data = [[Paragraph(h, header_style) for h in headers]] + chunk
        table = Table(data, colWidths=[60, 80, 80, 40, 60, 80, 95], repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        if i == 0:
            elements.append(Spacer(1, 100))
            elements.append(Paragraph("<u>Liste des Employés</u>", title_style))
            elements.append(Spacer(1, 20))

        elements.append(table)

        if start + MAX_ROWS_PER_PAGE < len(all_rows):
            elements.append(PageBreak())

    final_buffer = BytesIO()
    doc = SimpleDocTemplate(final_buffer, pagesize=A4, topMargin=180, leftMargin=50, rightMargin=50, bottomMargin=80)

    # --- Canvas personnalisé pour en-tête et pied ---
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
                # En-tête uniquement sur la première page
                if i == 0:
                    generer_entete_structure_pdf(self, structure)
                # Pied de page uniquement sur la dernière page
                if i == len(self._saved_page_states) - 1:
                    generer_pied_structure_pdf(self)  # <-- sans argument
                canvas.Canvas.showPage(self)
            canvas.Canvas.save(self)

    doc.build(elements, canvasmaker=CustomCanvas)
    #doc.build(elements, canvasmaker=HeaderFooterCanvas)

    response = HttpResponse(final_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="liste_employes.pdf"'
    return response



def get_styles():
    styles = getSampleStyleSheet()
    return {
        'title': ParagraphStyle(name='TitleTimes', parent=styles['Title'], fontName='Times-Bold', fontSize=18, leading=22),
        'cell': ParagraphStyle(name='CellStyleTimes', fontName='Times-Roman', fontSize=12, leading=14),
        'header': ParagraphStyle(name='HeaderStyleTimes', parent=styles['Normal'], fontName='Times-Bold', fontSize=12, alignment=1)
    }


def build_employe_infos_pdf(employe, structure, styles):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=280, leftMargin=50, rightMargin=50, bottomMargin=50)

    # Styles avec fallback
    title_style = styles.get('title') or styles.get('Title') or ParagraphStyle('title', fontName='Times-Bold', fontSize=16)
    cell_style = styles.get('cell') or styles.get('BodyText') or ParagraphStyle('cell', fontName='Times-Roman', fontSize=10)

    elements = [
        Spacer(1, 20),
        Paragraph(f"Fiche complète de l'employé : {employe.last_name} {employe.first_name}", title_style),
        Spacer(1, 20)
    ]

    data = [
        ["Champ", "Valeur"],
        ["Matricule", employe.matricule or ""],
        ["Nom", employe.last_name or ""],
        ["Prénom", employe.first_name or ""],
        ["Sexe", employe.get_sexe_display() if hasattr(employe, 'get_sexe_display') else ""],
        ["Statut", employe.get_statut_display() if hasattr(employe, 'get_statut_display') else ""],
        ["Statut utilisateur", employe.statut_user or ""],
        ["Email", employe.email or ""],
        ["Téléphone", employe.telephone or ""],
        ["Adresse", employe.adresse or ""],
        ["Date de naissance", str(employe.date_naissance) if employe.date_naissance else ""],
        ["Lieu de naissance", employe.lieu_naissance or ""],
        ["Nationalité", employe.nationalite or ""],
        ["Grade", str(employe.grade or "")],
        ["Echelle", str(employe.echelle or "")],
        ["Catégorie", str(employe.categorie or "")]
    ]

    table = Table(
        [[Paragraph(str(cell), cell_style) for cell in row] for row in data],
        colWidths=[150, 300]
    )
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (1, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # Ajout de la photo si elle existe et que le chemin est valide
    if employe.image and hasattr(employe.image, 'path') and os.path.exists(employe.image.path):
        elements.append(Paragraph("Photo de l'employé :", title_style))
        elements.append(Spacer(1, 6))
        elements.append(Image(employe.image.path, width=150, height=150))
        elements.append(Spacer(1, 20))

    # Fonction en-tête locale
    def en_tete_page(pdf_canvas, doc):
        if structure:
            generer_entete_structure_pdf(pdf_canvas, structure)

    # Construire le document en passant la fonction d’en-tête sur la première page
    doc.build(elements, onFirstPage=en_tete_page)

    buffer.seek(0)
    return buffer


# Importe tes modèles et fonctions nécessaires ici
# from .models import Employe, Structure
# from .utils_pdf import get_styles, build_employe_infos_pdf, generer_pdf_operations_employe, generer_pdf_affectations_employe, generer_pdf_absences_employe, generer_entete_structure_pdf, generer_pied_structure_pdf


def employe_print_list_operation(request, pk):
    employe = get_object_or_404(Employe, pk=pk)
    styles = get_styles()
    structure = Structure.objects.first()

    # 1) PDF portrait
    buffer_portrait = build_employe_infos_pdf(employe, structure, styles)
    buffer_portrait.seek(0)

    # 2) PDF paysage
    buffer_landscape = BytesIO()
    doc_landscape = SimpleDocTemplate(
        buffer_landscape,
        pagesize=landscape(A4),
        leftMargin=30,
        rightMargin=30,
        topMargin=80,     # un peu plus haut pour laisser place à l'en-tête
        bottomMargin=80   # on réserve la place du footer
    )

    # En-tête uniquement sur la première page
    def en_tete_page(pdf_canvas, doc):
        if structure:
            generer_entete_structure_pdf(pdf_canvas, structure)

    # Pied uniquement sur la dernière page
    def pied_derniere_page(pdf_canvas, doc):
        if doc.page == doc.pageCount:  # ✅ seulement sur la dernière page
            generer_pied_structure_pdf(pdf_canvas)

    # Définir le gabarit de page
    frame = Frame(
        doc_landscape.leftMargin,
        doc_landscape.bottomMargin,
        doc_landscape.width,
        doc_landscape.height,
        id="normal"
    )
    template = PageTemplate(id="AllPages", frames=[frame])
    doc_landscape.addPageTemplates([template])

    # Récupération des blocs de contenu
    ops_elements = generer_pdf_operations_employe(employe)
    abs_elements = generer_pdf_absences_employe(employe)

    if not isinstance(ops_elements, list)  or not isinstance(abs_elements, list):
        raise TypeError("Les fonctions doivent retourner une liste de Flowables")

    elements = ops_elements + abs_elements
    elements.append(Spacer(1, 30))  # petit espace

    # Construire le PDF
    doc_landscape.build(
        elements,
        onFirstPage=lambda c, d: (en_tete_page(c, d), pied_derniere_page(c, d)),
        onLaterPages=lambda c, d: pied_derniere_page(c, d)
    )

    buffer_landscape.seek(0)

    # 3) Fusion PDFs
    final_output = BytesIO()
    merger = PdfMerger()
    merger.append(PdfReader(buffer_portrait))
    merger.append(PdfReader(buffer_landscape))
    merger.write(final_output)
    merger.close()
    final_output.seek(0)

    # 4) Réponse HTTP
    response = HttpResponse(final_output.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="operation_employe_{employe.matricule}.pdf"'
    return response
