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


from Gestion_adherent.Cotisation_adherent.models import Cotisation
from Gestion_adherent.Inscription_adherent.suiviTuteurAdherent.models import SuiviTuteurAdherent
from Gestion_adherent.Prise_en_charge_adherent.views import adherent_prises_en_charge_print_pdf
from Gestion_personnel.operation.vew_print1 import generer_pied_structure_pdf
from referentiel.structure.models import Structure
from referentiel.structure.vew_impression import generer_entete_structure_pdf

from .models import Adherent


# ---------------------- Impression fiche individuelle ----------------------
def adherent_print_detail(request, pk):
    # Récupération des infos
    adherent = get_object_or_404(Adherent, pk=pk)
    structure = Structure.objects.first()

    # Réponse HTTP pour le PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="fiche_adherent_{adherent.id}.pdf"'

    # Configuration du document PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=200,
        leftMargin=30,
        rightMargin=30,
        bottomMargin=30,
    )

    elements = []
    styles = getSampleStyleSheet()

    # === STYLE DES TITRES ===
    title_style = ParagraphStyle(
        name='TitleTimes',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=18,
        leading=22,
        alignment=1,  # centré
        textColor=colors.HexColor("#2F4F4F")
    )

    # === STYLE DES CELLULES ===
    header_style = ParagraphStyle(
        name='HeaderStyleTimes',
        fontName='Times-Bold',
        fontSize=12,
        textColor=colors.white,
        alignment=1
    )

    cell_style = ParagraphStyle(
        name='CellStyleTimes',
        fontName='Times-Roman',
        fontSize=11,
        leading=14,
        alignment=1
    )

    # === Titre principal ===
    elements.append(Paragraph(f"Fiche Adhérent : {adherent.last_name} {adherent.first_name}", title_style))
    elements.append(Spacer(1, 20))

    # === CHAMPS À AFFICHER ===
    champs = [
        "Nom", "Prénom", "Date de naissance", "Lieu de naissance", "Téléphone",
        "Email", "Adresse", "Statut utilisateur", "Père", "Mère"
    ]

    # === VALEURS CORRESPONDANTES ===
    valeurs = [
        adherent.last_name or "Non renseigné",
        adherent.first_name or "Non renseigné",
        adherent.date_naissance.strftime('%d/%m/%Y') if adherent.date_naissance else "Non renseignée",
        adherent.lieu_naissance or "Non renseigné",
        adherent.telephone or "Non renseigné",
        adherent.email or "Non renseigné",
        adherent.adresse or "Non renseignée",
        adherent.statut_user.capitalize() or "Non renseigné",
        f"{str(adherent.pere)} " if adherent.pere else "Non renseigné",
        f"{str(adherent.mere)} " if adherent.mere else "Non renseigné",
    ]

    # === CONSTRUCTION DU TABLEAU ===
    # Ligne 1 = en-têtes / Ligne 2 = valeurs
    table_data = [
        [Paragraph(champ, header_style) for champ in champs],
        [Paragraph(valeur, cell_style) for valeur in valeurs]
    ]

    table = Table(table_data, colWidths=[70, 70, 90, 100, 80, 120, 120, 100, 100, 100])
    table.setStyle(TableStyle([
        # En-têtes
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),

        # Valeurs
        ("BACKGROUND", (0, 1), (-1, 1), colors.whitesmoke),
        ("TEXTCOLOR", (0, 1), (-1, 1), colors.black),
        ("ALIGN", (0, 1), (-1, 1), "CENTER"),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, 1), 9),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 6),

        # Bordures
        ("GRID", (0, 0), (-1, -1), 0.7, colors.grey),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 30))

    # === Pied de page ===
    elements.append(Paragraph("<i>Document généré automatiquement par le système AJCA</i>", styles["Normal"]))

    # === Gestion des entêtes ===
    def en_tete_page(pdf_canvas, doc):
        if structure:
            generer_entete_structure_pdf(pdf_canvas, structure)

    def pied_de_page(pdf_canvas, doc):
        pass

    # Génération finale du PDF
    doc.build(elements, onFirstPage=lambda c, d: (en_tete_page(c, d), pied_de_page(c, d)))
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return elements  # ⚠️ On retourne les flowables pour adherent_print_list_operation


# ---------------------- Impression liste des adhérents ----------------------
def adherent_print_list(request):
    adherents = Adherent.objects.filter(statut=Adherent.STATUT_ACTIF).order_by('-date_creation')
    structure = Structure.objects.first()
    MAX_ROWS_PER_PAGE = 15

    # Styles globaux
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=18,
        alignment=1,  # Centré
        spaceAfter=20
    )
    header_style = ParagraphStyle(
        'Header',
        fontName='Times-Bold',
        fontSize=10,
        alignment=1  # Centré
    )
    cell_style = ParagraphStyle(
        'Cell',
        fontName='Times-Roman',
        fontSize=9,
        alignment=1  # Centré pour uniformiser
    )

    # En-têtes du tableau
    headers = ["Nom", "Prénom", "Téléphone", "Email"]

    # Remplissage des données
    all_rows = []
    for ad in adherents:
        all_rows.append([
            Paragraph(ad.last_name or '', cell_style),
            Paragraph(ad.first_name or '', cell_style),
            Paragraph(ad.telephone or '', cell_style),
            Paragraph(ad.email or '', cell_style),
        ])

    elements = [Spacer(1, 30)]

    # Création des pages avec pagination
    for i, start in enumerate(range(0, len(all_rows), MAX_ROWS_PER_PAGE)):
        chunk = all_rows[start:start + MAX_ROWS_PER_PAGE]
        data = [[Paragraph(h, header_style) for h in headers]] + chunk

        # ✅ Tableau optimisé et équilibré
        table = Table(
            data,
            colWidths=[90, 90, 100, 140],  # Réduction largeur globale
            repeatRows=1
        )
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))

        # Ajout du titre uniquement sur la première page
        if i == 0:
            elements.append(Spacer(1, 130))
            elements.append(Paragraph("<u>Liste des Adhérents</u>", title_style))
            elements.append(Spacer(1, 15))

        # Ajout du tableau
        elements.append(table)

        # Page suivante si nécessaire
        if start + MAX_ROWS_PER_PAGE < len(all_rows):
            elements.append(PageBreak())

    # Génération du PDF
    final_buffer = BytesIO()

    def en_tete_page(pdf_canvas, doc):
        if structure:
            generer_entete_structure_pdf(pdf_canvas, structure)

    def pied_de_page(pdf_canvas, doc):
        generer_pied_structure_pdf(pdf_canvas)

    doc = SimpleDocTemplate(
        final_buffer,
        pagesize=A4,
        topMargin=150,
        leftMargin=40,
        rightMargin=40,
        bottomMargin=60
    )

    # ✅ Construction du document avec entête + pied de page
    doc.build(
        elements,
        onFirstPage=lambda c, d: (en_tete_page(c, d), pied_de_page(c, d)),
        onLaterPages=lambda c, d: pied_de_page(c, d)
    )

    # Réponse PDF
    response = HttpResponse(final_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="liste_adherents.pdf"'
    return response


# ---------------------- Impression fiche  opérations ----------------------
def adherent_print_list_operation(request, pk):
    adherent = get_object_or_404(Adherent, pk=pk)
    structure = Structure.objects.first()

    # === Portrait : fiche de l'adhérent ===
    portrait_elements = adherent_print_detail_print(request, pk)
    if not isinstance(portrait_elements, list):
        raise TypeError("La fonction adherent_print_detail_print doit retourner une liste de Flowables")

    buffer_portrait = None
    if portrait_elements:
        buffer_portrait = BytesIO()
        doc_portrait = SimpleDocTemplate(
            buffer_portrait,
            pagesize=A4,  # Portrait
            topMargin=50,
            leftMargin=50,
            rightMargin=50,
            bottomMargin=50
        )
        doc_portrait.build(portrait_elements)
        buffer_portrait.seek(0)

    # === Portrait : opérations, absences, prises en charge ===
    ops_elements = cotisation_print_detail(request, pk)
    abs_elements = suivi_print_detail(request, pk)
    prises_elements = adherent_prises_en_charge_print_pdf(pk)

    # Fusionner les Flowables
    all_elements = []
    for el in [ops_elements, abs_elements, prises_elements]:
        if not isinstance(el, list):
            raise TypeError("Toutes les fonctions doivent retourner une liste de Flowables")
        if el:
            all_elements.extend(el)

    buffer_all = None
    if all_elements:
        buffer_all = BytesIO()
        doc_all = SimpleDocTemplate(
            buffer_all,
            pagesize=A4,  # Portrait
            leftMargin=30,
            rightMargin=30,
            topMargin=80,
            bottomMargin=80
        )

        def en_tete_page(pdf_canvas, doc):
            if structure:
                generer_entete_structure_pdf(pdf_canvas, structure)

        def pied_de_page(pdf_canvas, doc):
            pass

        doc_all.build(
            all_elements,
            onFirstPage=lambda c, d: (en_tete_page(c, d), pied_de_page(c, d)),
            onLaterPages=lambda c, d: pied_de_page(c, d)
        )
        buffer_all.seek(0)

    # === Fusion des PDF ===
    final_output = BytesIO()
    merger = PdfMerger()

    if buffer_portrait:
        merger.append(PdfReader(buffer_portrait))
    if buffer_all:
        merger.append(PdfReader(buffer_all))

    merger.write(final_output)
    merger.close()
    final_output.seek(0)

    response = HttpResponse(final_output.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="operation_adherent_{adherent.id}.pdf"'
    return response


# === Fiche adhérent (portrait) ===
def adherent_print_detail(request, pk):
    adherent = get_object_or_404(Adherent, pk=pk)
    structure = Structure.objects.first()
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontName='Times-Bold', fontSize=16)
    cell_style = ParagraphStyle('Cell', fontName='Times-Roman', fontSize=12)

    elements = [Spacer(1, 250)]
    elements.append(Paragraph(f"Fiche Adhérent : {adherent.last_name} {adherent.first_name}", title_style))
    elements.append(Spacer(1, 12))

    data = [
        [Paragraph("Champ", title_style), Paragraph("Valeur", title_style)],
        [Paragraph("Nom", cell_style), Paragraph(adherent.last_name or '', cell_style)],
        [Paragraph("Prénom", cell_style), Paragraph(adherent.first_name or '', cell_style)],
        [Paragraph("Date de naissance", cell_style), Paragraph(adherent.date_naissance.strftime('%d/%m/%Y') if adherent.date_naissance else '', cell_style)],
        [Paragraph("Téléphone", cell_style), Paragraph(adherent.telephone or '', cell_style)],
        [Paragraph("Email", cell_style), Paragraph(adherent.email or '', cell_style)],
        [Paragraph("Adresse", cell_style), Paragraph(adherent.adresse or '', cell_style)],
    ]

    table = Table(data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))
    def en_tete_page(pdf_canvas, doc):
        if structure:
            generer_entete_structure_pdf(pdf_canvas, structure)

    def pied_de_page(pdf_canvas, doc):
        generer_pied_structure_pdf(pdf_canvas)

    
    # Génération PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=50, leftMargin=50, rightMargin=50, bottomMargin=50)
    doc.build(elements, onFirstPage=lambda c, d: (en_tete_page(c, d), pied_de_page(c, d)), onLaterPages=lambda c, d: pied_de_page(c, d))
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="fiche_adherent_{adherent.id}.pdf"'
    return response

def adherent_print_detail_print(request, pk):
    structure = Structure.objects.first()
    adherent = get_object_or_404(Adherent, pk=pk)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontName='Times-Bold', fontSize=16)
    cell_style = ParagraphStyle('Cell', fontName='Times-Roman', fontSize=12)
    buffer = BytesIO()
    doc_landscape = SimpleDocTemplate(buffer, pagesize=A4, topMargin=50, leftMargin=50, rightMargin=50, bottomMargin=50)
 
    elements = [Spacer(1, 12)]
    elements.append(Paragraph(f"Fiche Adhérent : {adherent.last_name} {adherent.first_name}", title_style))
    elements.append(Spacer(1, 12))

    data = [
        [Paragraph("Champ", title_style), Paragraph("Valeur", title_style)],
        [Paragraph("Nom", cell_style), Paragraph(adherent.last_name or '', cell_style)],
        [Paragraph("Prénom", cell_style), Paragraph(adherent.first_name or '', cell_style)],
        [Paragraph("Date de naissance", cell_style), Paragraph(adherent.date_naissance.strftime('%d/%m/%Y') if adherent.date_naissance else '', cell_style)],
        [Paragraph("Téléphone", cell_style), Paragraph(adherent.telephone or '', cell_style)],
        [Paragraph("Email", cell_style), Paragraph(adherent.email or '', cell_style)],
        [Paragraph("Adresse", cell_style), Paragraph(adherent.adresse or '', cell_style)],
    ]

    table = Table(data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))
    def en_tete_page(pdf_canvas, doc):
        if structure:
            generer_entete_structure_pdf(pdf_canvas, structure)

    def pied_de_page(pdf_canvas, doc):
        generer_pied_structure_pdf(pdf_canvas)

    doc_landscape.build(elements, onFirstPage=lambda c, d: (en_tete_page(c, d), pied_de_page(c, d)), onLaterPages=lambda c, d: pied_de_page(c, d))

    return elements

# === Cotisations (tableau paysage) ===
def cotisation_print_detail(request, pk):
    # On récupère soit une cotisation par PK, soit toutes celles de l'adhérent
    cotisations = list(Cotisation.objects.filter(adherent_id=pk))
    elements = []

    if cotisations:
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('Title', parent=styles['Title'], fontName='Times-Bold', fontSize=16)
        cell_style = ParagraphStyle('Cell', fontName='Times-Roman', fontSize=12)
        elements.append(Spacer(1, 230))
        elements.append(Paragraph("Détail des cotisations", title_style))
        elements.append(Spacer(1, 12))

        # En-tête du tableau
        data = [[Paragraph("Date", cell_style), Paragraph("Montant", cell_style),Paragraph("Adhérent", cell_style), Paragraph("Statut", cell_style)]]

        for c in cotisations:
            data.append([
                Paragraph(c.date_cotisation.strftime('%d/%m/%Y') if c.date_cotisation else '', cell_style),
                Paragraph(str(c.montant)+" FCFA" if c.montant else '', cell_style),
                Paragraph(str(c.adherent) or '', cell_style),
                Paragraph(c.statut.capitalize()or '', cell_style),
            ])

        table = Table(
            data,
            colWidths=[80, 80, 100, 110],  # ✅ Colonnes réduites
            splitByRow=1
        )
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(table)

    return elements


# === Suivi Tuteur (tableau paysage) ===
def suivi_print_detail(request, pk):
    suivis = SuiviTuteurAdherent.objects.filter(adherent_id=pk)
    elements = []

    if suivis.exists():
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('Title', parent=styles['Title'], fontName='Times-Bold', fontSize=16)
        cell_style = ParagraphStyle('Cell', fontName='Times-Roman', fontSize=12)
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Suivi du tuteur", title_style))
        elements.append(Spacer(1, 12))

        data = [[Paragraph("Adhérent",cell_style) ,Paragraph("Téléphone adhérent", cell_style),Paragraph("Date", cell_style),Paragraph("Tuteur", cell_style), Paragraph("Téléphone tuteur", cell_style)]]

        for s in suivis:
            data.append([
                Paragraph(str(s.adherent) or '', cell_style),
                Paragraph(str(s.adherent.telephone) or '', cell_style),
                Paragraph(s.date_creation.strftime('%d/%m/%Y') if s.date_creation else '', cell_style),
                Paragraph(str(s.tuteur) or '', cell_style),
                Paragraph(str(s.tuteur.telephone) or '', cell_style),
            ])

        table = Table(
            data,
            colWidths=[80, 80, 100, 120],  # ✅ Colonnes réduites
            splitByRow=1
        )

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # ✅ En-tête grisée
            ('GRID', (0, 0), (-1, -1), 1, colors.black),       # ✅ Bordures
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),            # ✅ Alignement vertical centré
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),             # ✅ Centrer le contenu
            ('FONTSIZE', (0, 0), (-1, -1), 9),                 # ✅ Police légèrement réduite
        ]))

        elements.append(table)

    return elements
