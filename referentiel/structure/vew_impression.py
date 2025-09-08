import re
from django.http import HttpResponse
from reportlab.pdfgen import canvas
import csv
import os
from django.conf import settings
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.utils.timezone import localtime
from textwrap import wrap  # <-- Pour couper le texte
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from Gestion_personnel.operation.vew_print1 import generer_pied_structure_pdf
from .models import Structure
from io import BytesIO
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
def generer_entete_structure_pdf(p):
    width, height = A4
    y = height - 60
    line_height = 15
    s = Structure.objects.first() 

    # Affichage du logo
    """   
    if s and s.logo_structure:
        logo_path = os.path.join(settings.MEDIA_ROOT, s.logo_structure.name)
        try:
            logo = ImageReader(logo_path)
            max_w, max_h = 120, 80
            iw, ih = logo.getSize()
            scale = min(max_w / iw, max_h / ih, 1)
            lw, lh = iw * scale, ih * scale
            x = (width - lw) / 2
            y_logo = height - lh - 20
            p.drawImage(logo, x, y_logo, width=lw, height=lh, mask='auto')
            y = y_logo - 30
        except Exception as e:
            print(f"Erreur affichage logo : {e}")
            p.setFont("Times-Roman", 10)
            p.drawCentredString(width / 2, y, "Logo non disponible")
            y -= 40
    else:
        p.setFont("Times-Roman", 10)
        p.drawCentredString(width / 2, y, "Logo non disponible")
        y -= 40
 """
    # Contenu dynamique
    if s:
        lignes = [
            s.pays_residence.upper(),
            s.devise_pays,
            "",
            "------------------------------"
        ]

        # Découper structure_sous_tutelle en plusieurs lignes si trop longue
        tutelle_lignes = wrap(s.structure_sous_tutelle.upper(), width=70)  # 70 est la limite de caractères
        lignes.extend(tutelle_lignes)

        lignes += [
            "------------------------------",
            s.direction_tutelle.upper(),
            "------------------------------",
            s.raison_sociale.upper(),
            "",
            f" : {s.matricule} / Adresse : {s.adresse}",
            f"Email : {s.email} – {s.lieu_residence}",
        ]
    else:
        lignes = ["Aucune information sur la structure disponible."]

    # Affichage des lignes centrées
    p.setFont("Times-Roman", 12)
    for ligne in lignes:
        p.drawCentredString(width / 2, y, ligne)
        y -= line_height

    y -= 30
    return y


# Définir les styles globaux
styles = getSampleStyleSheet()
styleN = styles['Normal']

# --- Classe personnalisée pour gérer en-tête, pied et pagination ---
class CustomCanvas(canvas.Canvas):
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

            # En-tête sur la première page uniquement
            if i == 0:
                generer_entete_structure_pdf(self, Structure.objects.first())

            # Pied sur la dernière page uniquement
            if i == total_pages - 1:
                generer_pied_structure_pdf(self)

            # Numéros de pages
            page_num_text = f"Page {i + 1} / {total_pages}"
            self.setFont("Times-Roman", 9)
            self.drawRightString(550, 20, page_num_text)

            super().showPage()
        super().save()


def generer_pdf_structure(request):
    structure = Structure.objects.first()
    if not structure:
        return HttpResponse("Aucune structure disponible", status=404)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="structure.pdf"'

    # Utiliser CustomCanvas
    p = CustomCanvas(response, pagesize=A4)
    width, height = A4
    margin_top = 60
    margin_bottom = 40
    x_start = 60
    y = height - margin_top
    cell_padding = 4

    # --- Titre principal ---
    p.setFont("Helvetica-Bold", 14)
    titre = "Informations générales"
    y -= 290
    p.drawCentredString(width / 2, y, titre)
    y -= 40

    # --- Données du tableau ---
    infos = [
        ['Attribut', 'Valeur'],
        ['Raison Sociale', structure.raison_sociale],
        ['Date Création', structure.date_creation.strftime('%d/%m/%Y %H:%M')],
        ['Adresse', structure.adresse],
        ['Email', structure.email],
        ['Téléphone', structure.telephone],
        ['Pays', structure.pays_residence],
        ['Matricule', structure.matricule],
        ['Lieu de Résidence', structure.lieu_residence],
    ]
    col_widths = [150, 350]

    # --- Fonction pour dessiner un tableau avec Paragraph et padding ---
    def draw_table(c, x, y, data, col_widths, row_height=18, padding=4):
        for row in data:
            # Calcul dynamique de la hauteur des lignes
            cell_heights = []
            for i, cell in enumerate(row):
                para = Paragraph(str(cell), styleN)
                w, h = para.wrap(col_widths[i] - 2 * padding, row_height)
                cell_heights.append(h)
            line_height = max(cell_heights) + 2 * padding

            # Nouvelle page si nécessaire
            if y - line_height < margin_bottom:
                c.showPage()
                y = height - margin_top

            # Dessiner chaque cellule
            x_pos = x
            for i, cell in enumerate(row):
                para = Paragraph(str(cell), styleN)
                w, h = para.wrap(col_widths[i] - 2 * padding, line_height)
                para.drawOn(c, x_pos + padding, y - h - padding)
                x_pos += col_widths[i]

            # Dessiner les bordures
            x_pos = x
            for w_cell in col_widths:
                c.rect(x_pos, y - line_height, w_cell, line_height, stroke=1, fill=0)
                x_pos += w_cell

            y -= line_height
        return y

    # --- Dessiner le tableau ---
    y = draw_table(p, x_start, y, infos, col_widths, padding=cell_padding)

    # Finalisation du PDF
    p.showPage()
    p.save()
    return response



def generer_sigle(texte):
    """
    Génère un sigle correct à partir du texte fourni,
    en ignorant les mots non pertinents comme 'de', 'du', etc.
    """
    # Mots à ignorer
    stopwords = {"de", "du", "des", "et", "la", "le", "les", "l", "l’", "d", "d’"}

    # On remplace les apostrophes par un espace pour bien séparer les mots
    texte = texte.replace("’", " ").replace("'", " ")

    # On divise le texte en mots en supprimant les caractères spéciaux
    mots = re.split(r"[ \t\n,;:.!?]+", texte)

    # On prend la première lettre des mots utiles uniquement
    sigle = "".join(
        mot[0] for mot in mots
        if mot and mot.lower() not in stopwords
    ).upper()

    return sigle

def generer_entete_structure_pdf(p, structure, numero=None):
    width, height = A4
    y = height - 60
    line_height = 15

    # Préparation des lignes principales
    lignes = [
        structure.pays_residence.upper(),
        structure.devise_pays,
        "",
        "------------------------------"
    ]

    # Ajout des informations de tutelle
    tutelle_lignes = wrap(structure.structure_sous_tutelle.upper(), width=70)
    lignes.extend(tutelle_lignes)

    # Ajout d'autres informations
    lignes += [
        "------------------------------",
        structure.direction_tutelle.upper(),
        "------------------------------",
        structure.raison_sociale.upper(),
        "",
        f" : {structure.matricule} / Adresse : {structure.adresse}",
        f"Email : {structure.email} – {structure.lieu_residence}",
    ]

    # Écriture des lignes dans le PDF
    p.setFont("Times-Roman", 12)
    for ligne in lignes:
        p.drawCentredString(width / 2, y, ligne)
        y -= line_height

    y -= 10  # petit espace avant la ligne

    # Ligne épaisse
    p.setLineWidth(3)
    p.line(50, y, width - 50, y)
    y -= 20

    # Génération du sigle correct de la tutelle
    tutelle_abbr = generer_sigle(structure.structure_sous_tutelle)

    # Récupération des 3 premières lettres de la direction
    direction_abbr = "".join(
        [c for c in structure.direction_tutelle if c.isalpha()]
    )[:3].upper()

    # Construire la chaîne avant et après le numéro
    prefixe = "N° "
    suffixe = f" {tutelle_abbr}-{direction_abbr} - Sce:perm"

    # Définir la police en gras
    p.setFont("Times-Bold", 14)

    # Position de départ pour le texte complet
    x_debut = 60

    # Si le numéro est vide, on ne l'affiche pas mais on réserve son espace
    numero_affiche = str(numero) if numero not in [None, "", "None"] else " " * 10

    texte_complet = prefixe + numero_affiche + suffixe
    p.drawString(x_debut, y, texte_complet)

    # Calcul de la largeur du préfixe
    largeur_prefixe = p.stringWidth(prefixe, "Times-Bold", 14)

    # Si numero est vide, on garde la longueur de l'espace réservé
    largeur_numero = (
        p.stringWidth(str(numero), "Times-Bold", 14)
        if numero not in [None, "", "None"]
        else p.stringWidth(" " * 10, "Times-Bold", 14)
    )

    # Tracer la ligne sous l'emplacement du numéro
    x_numero = x_debut + largeur_prefixe
    p.setLineWidth(1)
    p.line(x_numero, y - 2, x_numero + largeur_numero, y - 2)

    y -= line_height + 20  # espace final

    return y

def afficher_structure_direct(request, pk):
    structure = get_object_or_404(Structure, pk=pk)

    fonctions_data = []
    for fonction in structure.fonctions.all():
        parent = fonction.fonction_parent.designation if fonction.fonction_parent else "Aucune"
        fonctions_data.append({
            "designation": fonction.designation,
            "parent": parent
        })

    organisations_data = []
    for org in structure.organisations_unites.all():
        parent = org.organisation_unite_parent.designation if org.organisation_unite_parent else "Aucune"
        unite = org.unite.nom if hasattr(org.unite, 'nom') else str(org.unite)
        organisations_data.append({
            "designation": org.designation,
            "unite": unite,
            "parent": parent
        })

    return {
        "structure": structure,
        "fonctions": fonctions_data,
        "organisations": organisations_data
    }


def draw_table(p, x, y, data, col_widths, row_height=36, repeat_header=True, max_lines_per_cell=2):
    """
    Dessine un tableau simple avec bordures, entête en gras.
    Supporte le retour à la ligne dans les cellules.
    row_height correspond à la hauteur d'une ligne simple,
    on double la hauteur pour accommoder 2 lignes max par cellule.

    repeat_header = True => répète l'entête à chaque nouvelle page.

    Retourne la nouvelle position y après le tableau.
    """
    n_rows = len(data)
    n_cols = len(data[0]) if n_rows > 0 else 0
    table_width = sum(col_widths)
    page_height = A4[1]
    margin_bottom = 40

    # Hauteur d'une "ligne" de texte simple
    single_line_height = row_height / max_lines_per_cell

    for row_i, row in enumerate(data):
        # Avant d'écrire la ligne, vérifier l'espace restant (hauteur de la ligne)
        if y - row_height < margin_bottom:
            p.showPage()
            y = page_height - 40
            # Répéter entête si demandé (sauf 1ère ligne)
            if repeat_header and row_i != 0:
                p.setFont("Helvetica-Bold", 11)
                text_x = x + 5
                yi = y - 14
                for col_i in range(n_cols):
                    p.drawString(text_x + sum(col_widths[:col_i]), yi, str(data[0][col_i]))
                # Bordures entête
                p.line(x, y, x + table_width, y)
                p.line(x, y - row_height, x + table_width, y - row_height)
                col_x = x
                for w in col_widths:
                    p.line(col_x, y, col_x, y - row_height)
                    col_x += w
                p.line(col_x, y, col_x, y - row_height)
                y -= row_height
            else:
                y -= 0

        # Bordures horizontales
        p.line(x, y, x + table_width, y)
        p.line(x, y - row_height, x + table_width, y - row_height)
        # Bordures verticales
        col_x = x
        for w in col_widths:
            p.line(col_x, y, col_x, y - row_height)
            col_x += w
        p.line(col_x, y, col_x, y - row_height)

        text_x = x + 5
        base_y = y - 14

        # Entête en gras
        if row_i == 0:
            p.setFont("Helvetica-Bold", 11)
        else:
            p.setFont("Helvetica", 11)

        # Pour chaque cellule, on wrap le texte selon la largeur max approximative
        for col_i, cell in enumerate(row):
            max_chars = int(col_widths[col_i] / 6)  # approx 6 pts par caractère
            lines = wrap(str(cell), width=max_chars)
            # limiter à max_lines_per_cell lignes
            lines = lines[:max_lines_per_cell]

            for line_i, line in enumerate(lines):
                # Décaler verticalement par ligne
                p.drawString(text_x + sum(col_widths[:col_i]), base_y - line_i * single_line_height, line)

        y -= row_height

    return y - 10


def generer_pdf_structure_detail(request, pk):
    data = afficher_structure_direct(request, pk)
    structure = data["structure"]
    fonctions = data["fonctions"]
    organisations = data["organisations"]

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=50, leftMargin=50,
                            topMargin=100, bottomMargin=60)
    styles = getSampleStyleSheet()
    styleH = styles['Heading1']
    styleN = styles['Normal']
    elements = []

    # --- Titre général ---
    elements.append(Spacer(1, 200))
    elements.append(Paragraph("<b>Informations générales</b>", styleH))
    elements.append(Spacer(1, 10))

    # Fonction pour créer un Paragraph pour contenu de cellule
    def wrap_text(text, style=styleN):
        if text is None:
            text = ""
        return Paragraph(str(text), style)

    # --- Tableau infos de base ---
    infos = [
        [wrap_text('Attribut'), wrap_text('Valeur')],
        [wrap_text('Raison Sociale'), wrap_text(structure.raison_sociale)],
        [wrap_text('Date Création'), wrap_text(structure.date_creation.strftime('%d/%m/%Y %H:%M'))],
        [wrap_text('Adresse'), wrap_text(structure.adresse)],
        [wrap_text('Email'), wrap_text(structure.email)],
        [wrap_text('Téléphone'), wrap_text(structure.telephone)],
        [wrap_text('Pays'), wrap_text(structure.pays_residence)],
        [wrap_text('Matricule'), wrap_text(structure.matricule)],
        [wrap_text('Lieu de Résidence'), wrap_text(structure.lieu_residence)],
    ]

    table = Table(infos, colWidths=[150, 350], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # --- Fonctions associées ---
    elements.append(Paragraph("<b>Fonctions associées</b>", styleH))
    elements.append(Spacer(1, 10))
    if fonctions:
        table_fonctions = [[wrap_text("Désignation"), wrap_text("Lien hiérarchique")]] + [
            [wrap_text(f['designation']), wrap_text(f['parent'])] for f in fonctions
        ]
        t_f = Table(table_fonctions, colWidths=[250, 220], repeatRows=1)
        t_f.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        elements.append(t_f)
        elements.append(Spacer(1, 20))
    else:
        elements.append(Paragraph("Aucune fonction.", styleN))
        elements.append(Spacer(1, 20))

    # --- Organisations associées ---
    elements.append(Paragraph("<b>Organisations d’unité associées</b>", styleH))
    elements.append(Spacer(1, 10))
    if organisations:
        table_orgs = [[wrap_text("Désignation"), wrap_text("Unité"), wrap_text("Lien hiérarchique")]] + [
            [wrap_text(o['designation']), wrap_text(o['unite']), wrap_text(o['parent'])] for o in organisations
        ]
        t_o = Table(table_orgs, colWidths=[180, 150, 140], repeatRows=1)
        t_o.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        elements.append(t_o)
    else:
        elements.append(Paragraph("Aucune organisation d’unité.", styleN))

    # --- Canvas personnalisé pour en-tête et pied ---
    class CustomCanvas(canvas.Canvas):
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


    doc.build(elements, canvasmaker=CustomCanvas)
    buffer.seek(0)
    return HttpResponse(buffer, content_type="application/pdf")
