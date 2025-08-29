from django.http import HttpResponse
from graphviz import Digraph
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
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
    elements.append(Spacer(1, 20))
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

def fonction_print_hierarchique(request):
    fonctions = Fonction.objects.all()

    # PDF setup
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="organigramme_fonctions.pdf"'

    c = canvas.Canvas(response, pagesize=landscape(A4))
    width, height = landscape(A4)

    box_width = 120
    box_height = 30
    x_margin = 50
    y_margin = 50

    # Ajouter le titre
    titre = "Organigramme des Fonctions"
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2, height - 30, titre)
    y_start = height - 60  # décaler le dessin des boîtes en dessous du titre

    # Construire la hiérarchie parent -> enfants
    hierarchy = {}
    for f in fonctions:
        parent_id = f.fonction_parent_id if f.fonction_parent else None
        hierarchy.setdefault(parent_id, []).append(f)

    # Fonction récursive pour calculer la largeur totale de chaque sous-arbre
    def compute_width(fonction):
        enfants = hierarchy.get(fonction.id, [])
        if not enfants:
            return 1
        return sum([compute_width(e) for e in enfants])

    # Fonction pour dessiner une ligne collée aux boîtes
    def draw_arrow(c, x_start, y_start, x_end, y_end):
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.line(x_start, y_start, x_end, y_end)

    # Style pour Paragraph (texte avec retour à la ligne)
    style = ParagraphStyle(
        'box_style',
        fontName='Helvetica',
        fontSize=10,
        leading=12,
        alignment=1  # centré horizontalement
    )

    # Fonction récursive pour dessiner les boîtes et les lignes
    def draw_tree(fonction, x_center, y_top):
        # Créer le texte comme Paragraph pour retour à la ligne automatique
        p = Paragraph(fonction.designation, style)
        text_width, text_height = p.wrap(box_width, 1000)

        # Ajuster la hauteur de la boîte si nécessaire
        current_box_height = max(box_height, text_height + 4)

        # Dessiner la boîte
        c.setFillColor(colors.lightblue)
        c.rect(x_center - box_width/2, y_top - current_box_height, box_width, current_box_height, fill=1)

        # Dessiner le texte centré verticalement
        p.drawOn(c, x_center - box_width/2, y_top - text_height - (current_box_height - text_height)/2)

        positions[fonction.id] = (x_center, y_top - current_box_height)

        # Dessiner les enfants
        enfants = hierarchy.get(fonction.id, [])
        if not enfants:
            return

        total_width = sum([compute_width(e) for e in enfants])
        spacing = box_width + 40
        start_x = x_center - (total_width/2)*spacing + spacing/2

        for e in enfants:
            child_width = compute_width(e)
            child_x = start_x + (child_width - 1)/2 * spacing
            child_y = y_top - current_box_height - 60
            draw_tree(e, child_x, child_y)
            draw_arrow(c, x_center, y_top - current_box_height + 1, child_x, child_y)
            start_x += child_width * spacing

    # Identifier les racines et dessiner
    positions = {}
    racines = hierarchy.get(None, [])
    if racines:
        total_width = sum([compute_width(r) for r in racines])
        spacing = box_width + 40
        start_x = x_margin + (width - 2*x_margin - total_width*spacing)/2 + spacing/2

        for r in racines:
            root_width = compute_width(r)
            x_center = start_x + (root_width - 1)/2 * spacing
            draw_tree(r, x_center, y_start)
            start_x += root_width * spacing

    c.showPage()
    c.save()
    return response
