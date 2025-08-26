from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from datetime import datetime

from referentiel.structure.models import Structure
from referentiel.structure.vew_impression import generer_entete_structure_pdf
from .models import Unite


def unite_print(request):
    # Préparer la réponse HTTP en PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="liste_unites.pdf"'

    # Création du document PDF avec marges pour entête/pied
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        topMargin=280,    # espace pour en-tête
        leftMargin=50,
        rightMargin=50,
        bottomMargin=50,  # espace pour pied de page
    )

    elements = []

    # Styles pour titres et cellules avec Times New Roman
    styles = getSampleStyleSheet()

    # Modifier le style Title pour utiliser Times-Roman
    title_style = ParagraphStyle(
        name='TitleTimes',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=18,
        leading=22,
    )
    title = Paragraph("Liste des Unités", title_style)
    elements.append(title)
    elements.append(Spacer(1, 20))

    # Style pour les cellules du tableau (Times New Roman normal)
    cell_style = ParagraphStyle(
        name='CellStyleTimes',
        fontName='Times-Roman',
        fontSize=10,
        leading=12,
        wordWrap='CJK',
    )

    # Préparer les données du tableau avec titres en gras Times New Roman
    header_style = ParagraphStyle(
        name='HeaderStyleTimes',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        alignment=1,  # centre
    )

    data = [
        [
            Paragraph("Désignation", header_style),
            Paragraph("Unité Parent", header_style),
        ]
    ]

    # Récupérer et trier les unités
    unites = Unite.objects.all().order_by('unite_parent__designation', 'designation')
    for unite in unites:
        designation = Paragraph(unite.designation, cell_style)
        parent = Paragraph(unite.unite_parent.designation if unite.unite_parent else "Aucune", cell_style)
        data.append([designation, parent])

    # Création du tableau avec largeur fixée, style coloré et grille
    table = Table(data, colWidths=[250, 250])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),

        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # en-tête centré
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),   # contenu aligné à gauche

        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),

        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    # Fonction pour dessiner l'en-tête sur chaque page
    def en_tete_page(pdf_canvas, doc):
        structure = Structure.objects.first()
        if structure:
            generer_entete_structure_pdf(pdf_canvas, structure)

    # Fonction pour dessiner le pied de page avec lieu + date/heure en Times Italic
    def pied_de_page(pdf_canvas, doc):
        structure = Structure.objects.first()
        if structure:
            texte = f"{structure.lieu_residence} , le  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            pdf_canvas.saveState()
            pdf_canvas.setFont("Times-Italic", 8)
            width, height = A4
            pdf_canvas.drawString(50, 30, texte)  # position : 50 pts à gauche, 30 pts du bas
            pdf_canvas.restoreState()

    # Combinaison des deux pour chaque page
    def on_page(pdf_canvas, doc):
        en_tete_page(pdf_canvas, doc)
        pied_de_page(pdf_canvas, doc)

    # Génération du PDF
    doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)

    return response
