from django.http import HttpResponse
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from datetime import datetime

from referentiel.organisation_unite.models import OrganisationUnite
from referentiel.structure.models import Structure
from referentiel.structure.vew_impression import generer_entete_structure_pdf


def organisation_unite_print(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="liste_organisations_unites.pdf"'

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
    title = Paragraph("Liste des Organisations d'Unités", title_style)
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
        alignment=1,  # center
    )

    # Préparer les données du tableau avec titres
    data = [
        [
            Paragraph("Désignation", header_style),
            Paragraph("Organisation Parent", header_style),
            Paragraph("Unité", header_style),
            Paragraph("Structure", header_style),
            Paragraph("Date de Création", header_style),
        ]
    ]

    organisations = OrganisationUnite.objects.all().order_by(
        'structure__raison_sociale',
        'organisation_unite_parent__designation',
        'designation'
    )

    for org in organisations:
        designation = Paragraph(org.designation, cell_style)
        parent = Paragraph(org.organisation_unite_parent.designation if org.organisation_unite_parent else "Aucune", cell_style)
        unite = Paragraph(org.unite.designation if org.unite else "N/A", cell_style)
        structure = Paragraph(org.structure.raison_sociale if org.structure else "N/A", cell_style)
        date_creation = Paragraph(org.date_creation.strftime('%d/%m/%Y'), cell_style)
        data.append([designation, parent, unite, structure, date_creation])

    table = Table(data, colWidths=[110, 110, 110, 110, 90])
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

def organisation_print_hierarchique(request):
    # Récupérer toutes les organisations
    organisations = OrganisationUnite.objects.all()

    # PDF setup
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="organigramme_services.pdf"'

    c = canvas.Canvas(response, pagesize=landscape(A4))
    width, height = landscape(A4)

    box_width = 120
    box_height = 30
    x_margin = 50
    y_margin = 50

    # Ajouter le titre
    titre = "Organigramme des services"
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2, height - 30, titre)
    y_start = height - 60  # décaler le dessin des boîtes sous le titre

    # Construire la hiérarchie parent -> enfants
    hierarchy = {}
    for org in organisations:
        parent_id = org.organisation_unite_parent_id if org.organisation_unite_parent else None
        hierarchy.setdefault(parent_id, []).append(org)

    # Fonction récursive pour calculer la largeur totale de chaque sous-arbre
    def compute_width(org):
        enfants = hierarchy.get(org.id, [])
        if not enfants:
            return 1
        return sum([compute_width(e) for e in enfants])

    # Fonction pour dessiner une ligne collée aux boîtes
    def draw_arrow(c, x_start, y_start, x_end, y_end):
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.line(x_start, y_start, x_end, y_end)

    # Style de texte avec retour à la ligne
    style = ParagraphStyle(
        'box_style',
        fontName='Helvetica',
        fontSize=10,
        leading=12,  # hauteur d'une ligne
        alignment=1  # centré horizontalement
    )

    # Fonction récursive pour dessiner les boîtes et les lignes
    def draw_tree(org, x_center, y_top):
        p = Paragraph(org.designation, style)
        text_width, text_height = p.wrap(box_width, 1000)

        current_box_height = max(box_height, text_height + 4)

        # Dessiner la boîte
        c.setFillColor(colors.lightblue)
        c.rect(x_center - box_width/2, y_top - current_box_height, box_width, current_box_height, fill=1)

        # Dessiner le texte centré
        p.drawOn(c, x_center - box_width/2, y_top - text_height - (current_box_height - text_height)/2)

        positions[org.id] = (x_center, y_top - current_box_height)

        enfants = hierarchy.get(org.id, [])
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

    # Dessiner les racines
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
