from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from datetime import datetime

from .models import Fonction
from referentiel.structure.models import Structure
from referentiel.structure.vew_impression import generer_entete_structure_pdf


def fonction_print(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="liste_fonctions.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        topMargin=280,   # marge haute pour laisser place à l'en-tête
        leftMargin=50,
        rightMargin=50,
        bottomMargin=50, # marge basse pour pied de page
    )

    elements = []

    styles = getSampleStyleSheet()

    # Titre en Times-Bold
    title_style = ParagraphStyle(
        name='TitleTimes',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=18,
        leading=22,
    )
    title = Paragraph("Liste des Fonctions", title_style)
    elements.append(title)
    elements.append(Spacer(1, 20))

    # Style cellule en Times-Roman avec retour à la ligne
    cell_style = ParagraphStyle(
        name='CellStyleTimes',
        fontName='Times-Roman',
        fontSize=10,
        leading=12,
        wordWrap='CJK',
    )

    # Style header en Times-Bold centré
    header_style = ParagraphStyle(
        name='HeaderStyleTimes',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        alignment=1,  # 1 = center
    )

    data = [
        [
            Paragraph("Désignation", header_style),
            Paragraph("Fonction Parent", header_style),
            Paragraph("Structure", header_style),
        ]
    ]

    fonctions = Fonction.objects.all().order_by(
        'structure__raison_sociale', 'fonction_parent__designation', 'designation'
    )

    for fonction in fonctions:
        designation = Paragraph(fonction.designation, cell_style)
        parent = Paragraph(fonction.fonction_parent.designation if fonction.fonction_parent else "Aucune", cell_style)
        structure = Paragraph(fonction.structure.raison_sociale if fonction.structure else "N/A", cell_style)
        data.append([designation, parent, structure])

    table = Table(data, colWidths=[180, 180, 180])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),

        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),   # en-tête centré
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),    # contenu aligné à gauche

        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),

        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    # Fonction pour dessiner l'en-tête
    def en_tete_page(pdf_canvas, doc):
        structure = Structure.objects.first()
        if structure:
            generer_entete_structure_pdf(pdf_canvas, structure)

    # Fonction pour dessiner le pied de page
    def pied_de_page(pdf_canvas, doc):
        structure = Structure.objects.first()
        if structure:
            texte = f"{structure.lieu_residence} , le  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            pdf_canvas.saveState()
            pdf_canvas.setFont("Times-Italic", 8)
            width, height = A4
            pdf_canvas.drawString(50, 30, texte)
            pdf_canvas.restoreState()

    # Combinaison des deux sur chaque page
    def on_page(pdf_canvas, doc):
        en_tete_page(pdf_canvas, doc)
        pied_de_page(pdf_canvas, doc)

    # Générer le PDF
    doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)

    return response
