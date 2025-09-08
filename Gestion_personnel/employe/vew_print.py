from datetime import datetime
from io import BytesIO
import os
from reportlab.pdfgen import canvas as rcanvas

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image,
    Frame,
    PageTemplate,
    PageBreak,
)


from PyPDF2 import PdfMerger, PdfReader

# Importations des fonctions personnalisées
from Gestion_personnel.absence.vew_print import generer_pdf_absences_employe
from Gestion_personnel.operation.vew_print1 import generer_pdf_operations_employe
from Gestion_personnel.operation.views import generer_pied_structure_pdf
from referentiel.structure.models import Structure
from referentiel.structure.vew_impression import generer_entete_structure_pdf
from Gestion_personnel.employe.models import Employe

from io import BytesIO
import os
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

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

    # Données du tableau
    data_left = [
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

    # Tableau des informations (colonne gauche)
    info_table = Table(
        [[Paragraph(str(cell), cell_style) for cell in row] for row in data_left],
        colWidths=[120, 220]
    )
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (1, 1), (-1, -1), colors.whitesmoke),
    ]))

    # Préparer la photo si elle existe
    photo_flowable = None
    if employe.image and hasattr(employe.image, 'path') and os.path.exists(employe.image.path):
        photo_flowable = Image(employe.image.path, width=150, height=150)

    # Tableau principal avec photo intégrée dans la cellule de droite
    main_table_data = [[info_table, photo_flowable if photo_flowable else ""]]
    main_table = Table(main_table_data, colWidths=[350, 150])
    main_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),  # centrer la photo dans sa cellule
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(main_table)
    elements.append(Spacer(1, 20))

    # Fonctions en-tête et pied de page
    def en_tete_page(pdf_canvas, doc):
        if structure:
            generer_entete_structure_pdf(pdf_canvas, structure)

    def pied_de_page(pdf_canvas, doc):
        if structure:
            generer_pied_structure_pdf(pdf_canvas)

    def on_page(pdf_canvas, doc):
        en_tete_page(pdf_canvas, doc)
        pied_de_page(pdf_canvas, doc)

    doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)

    return response


def employe_print_list(request):
    # Récupérer les employés actifs
    employes = Employe.objects.filter(statut=Employe.STATUT_ACTIF).order_by('matricule')
    employe_counts = employes.count()
    structure = Structure.objects.first()

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=18,
        alignment=1,
        spaceAfter=20
    )
    header_style = ParagraphStyle('Header', fontName='Times-Bold', fontSize=10, alignment=1)
    cell_style = ParagraphStyle('Cell', fontName='Times-Roman', fontSize=9)

    # En-têtes du tableau
    headers = ["Matricule", "Nom", "Prénom", "Sexe", "Statut", "Téléphone", "Email"]

    # Lignes du tableau
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

    # Préparer les éléments du PDF
    elements = []
    elements.append(Spacer(1, 250))
    elements.append(Paragraph("<u>Liste des Employés</u>", title_style))
    elements.append(Spacer(1, 20))

    # Construire le tableau
    data = [[Paragraph(h, header_style) for h in headers]] + all_rows
    table = Table(data, colWidths=[60, 80, 80, 60, 40, 80, 120], repeatRows=1)
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

    elements.append(table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Total des Employés : {employe_counts}", cell_style))

    # Préparer la réponse HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="liste_employes.pdf"'

    # Utiliser la réponse directement dans SimpleDocTemplate
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        topMargin=50,
        leftMargin=50,
        rightMargin=50,
        bottomMargin=50,
    )

    # Classe pour gérer l'en-tête et le pied de page
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

    # Construire le PDF
    doc.build(elements, canvasmaker=CustomCanvas)

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
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=280,
        leftMargin=50,
        rightMargin=50,
        bottomMargin=50
    )

    # Styles avec fallback
    title_style = styles.get('title') or styles.get('Title') or ParagraphStyle(
        'title', fontName='Times-Bold', fontSize=16
    )
    cell_style = styles.get('cell') or styles.get('BodyText') or ParagraphStyle(
        'cell', fontName='Times-Roman', fontSize=10
    )

    elements = [
        Spacer(1, 20),
        Paragraph(f"Fiche complète de l'employé : {employe.last_name} {employe.first_name}", title_style),
        Spacer(1, 20)
    ]

    # Données du tableau
    data_left = [
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

    # Tableau des informations (colonne gauche)
    info_table = Table(
        [[Paragraph(str(cell), cell_style) for cell in row] for row in data_left],
        colWidths=[120, 220]
    )
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (1, 1), (-1, -1), colors.whitesmoke),
    ]))

    # Préparer la photo si elle existe
    photo_flowable = None
    if employe.image and hasattr(employe.image, 'path') and os.path.exists(employe.image.path):
        photo_flowable = Image(employe.image.path, width=150, height=150)

    # Tableau principal avec photo intégrée dans la cellule de droite
    main_table_data = [[info_table, photo_flowable if photo_flowable else ""]]
    main_table = Table(main_table_data, colWidths=[350, 150])
    main_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),  # centrer la photo dans sa cellule
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(main_table)
    elements.append(Spacer(1, 20))

    # Classe CustomCanvas pour gérer en-tête, pied et numérotation
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

                # En-tête sur la première page
                if i == 0 and structure:
                    generer_entete_structure_pdf(self, structure)

                # Pied sur la dernière page
                if i == total_pages - 1 and structure:
                    generer_pied_structure_pdf(self)

                # Numéro de page en bas à droite
                self.setFont("Times-Roman", 9)
                self.drawRightString(480, 20, f"Page {i + 1} / {total_pages}")  # Ajusté pour A4 portrait

                super().showPage()
            super().save()

    # Construire le document avec CustomCanvas
    doc.build(elements, canvasmaker=CustomCanvas)
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
        topMargin=80,
        bottomMargin=80
    )

    # Classe CustomCanvas pour gérer en-tête, pied et numérotation
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

                # En-tête sur la première page
                if i == 0 and structure:
                    generer_entete_structure_pdf(self, structure)

                # Pied sur la dernière page
                if i == total_pages - 1 and structure:
                    generer_pied_structure_pdf(self)

                # Numéro de page en bas à droite
                self.setFont("Times-Roman", 9)
                self.drawRightString(780, 20, f"Page {i + 1} / {total_pages}")  # Ajuster selon landscape(A4)

                super().showPage()
            super().save()

    # Frame et PageTemplate
    frame = Frame(doc_landscape.leftMargin, doc_landscape.bottomMargin,
                  doc_landscape.width, doc_landscape.height, id="normal")
    template = PageTemplate(id="AllPages", frames=[frame])
    doc_landscape.addPageTemplates([template])

    # Récupération du contenu
    ops_elements = generer_pdf_operations_employe(employe)
    abs_elements = generer_pdf_absences_employe(employe)

    if not all(isinstance(el, list) for el in [ops_elements, abs_elements]):
        raise TypeError("Les fonctions doivent retourner une liste de Flowables")

    elements = ops_elements + abs_elements
    elements.append(Spacer(1, 30))

    # Construire le PDF paysage avec CustomCanvas
    doc_landscape.build(elements, canvasmaker=CustomCanvas)

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
