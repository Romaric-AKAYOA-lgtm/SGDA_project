from io import BytesIO
import re
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from textwrap import wrap
from referentiel.structure.models import Structure
from Gestion_personnel.operation.vew_print1 import generer_pied_structure_pdf

def generer_sigle(texte):
    stopwords = {"de", "du", "des", "et", "la", "le", "les", "l", "l’", "d", "d’"}
    texte = texte.replace("’", " ").replace("'", " ")
    mots = [mot for mot in re.split(r"[ \t\n,;:.!?]+", texte) if mot]
    return "".join(mot[0] for mot in mots if mot.lower() not in stopwords).upper()

def generer_entete_structure_pdf(p, structure, numero=None):
    width, height = A4
    y = height - 60
    line_height = 15

    lignes = [
        structure.pays_residence.upper(),
        structure.devise_pays,
        "",
        "------------------------------"
    ]
    tutelle_lignes = wrap(structure.structure_sous_tutelle.upper(), width=70)
    lignes.extend(tutelle_lignes)
    lignes += [
        "------------------------------",
        structure.direction_tutelle.upper(),
        "------------------------------",
        structure.raison_sociale.upper(),
        "",
        f" : {structure.matricule} / Adresse : {structure.adresse}",
        f"Email : {structure.email} – {structure.lieu_residence}",
    ]

    p.setFont("Times-Bold", 12)
    for ligne in lignes:
        p.drawCentredString(width / 2, y, ligne)
        y -= line_height

    y -= 10
    p.setLineWidth(3)
    p.line(50, y, width - 50, y)
    y -= 20

    tutelle_abbr = generer_sigle(structure.structure_sous_tutelle)
    direction_abbr = "".join([c for c in structure.direction_tutelle if c.isalpha()])[:3].upper()
    prefixe = "N° "
    suffixe = f" {tutelle_abbr}-{direction_abbr} - Sce:perm"
    p.setFont("Times-Bold", 14)

    x_debut = 60
    numero_affiche = str(numero) if numero not in [None, "", "None"] else " " * 10
    texte_complet = prefixe + numero_affiche + suffixe
    p.drawString(x_debut, y, texte_complet)

    largeur_prefixe = p.stringWidth(prefixe, "Times-Bold", 14)
    largeur_numero = p.stringWidth(numero_affiche, "Times-Bold", 14)
    x_numero = x_debut + largeur_prefixe
    p.setLineWidth(1)
    p.line(x_numero, y - 2, x_numero + largeur_numero, y - 2)

    y -= line_height + 20
    return y

from io import BytesIO
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from textwrap import wrap
from .models import Structure

from io import BytesIO
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from .models import Structure
def generer_pdf_structure(request):
    structures = Structure.objects.all()
    if not structures.exists():
        return HttpResponse("Aucune structure disponible", status=404)

    buffer = BytesIO()
    width, height = A4

    x_start = 50
    row_height = 20
    col_widths = [150, 350]
    padding_h = 4
    padding_v = 4

    styles = getSampleStyleSheet()
    styleN = styles['Normal']

    # ---- Classe personnalisée pour en-tête, pied et titre ----
    class CustomCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            self.structure = kwargs.pop("structure", None)
            super().__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total_pages = len(self._saved_page_states)
            for i, state in enumerate(self._saved_page_states):
                self.__dict__.update(state)

                # En-tête
                if self.structure:
                    generer_entete_structure_pdf(self, self.structure)

                # Titre centré avec espace
                self.setFont("Helvetica-Bold", 16)
                titre_y = height - 320  # ajuster ici pour descendre le titre
                self.drawCentredString(width / 2, titre_y, "Détails de la Structure")

                # Pied sur la dernière page
                if i == total_pages - 1:
                    generer_pied_structure_pdf(self)

                # Numéro de page
                page_num_text = f"Page {i + 1} / {total_pages}"
                self.setFont("Times-Roman", 9)
                self.drawRightString(width - 50, 20, page_num_text)

                super().showPage()
            super().save()
  
    for structure in structures:
        p = CustomCanvas(buffer, pagesize=A4, structure=structure)
        y = height -350  # ajuster ici pour descendre le tableau sous le titre

        infos = [
            ['Attribut', 'Valeur'],
            ['Raison Sociale', structure.raison_sociale],
            ['Date Création', structure.date_creation.strftime('%d/%m/%Y %H:%M')],
            ['Adresse', structure.adresse],
            ['Email', structure.email],
            ['Téléphone', structure.telephone],
            ['Pays', structure.pays_residence],
            ['Devise du Pays', structure.devise_pays],
            ['Direction de Tutelle', structure.direction_tutelle],
            ['Structure sous Tutelle', structure.structure_sous_tutelle],
            ['Matricule', structure.matricule],
            ['Lieu de Résidence', structure.lieu_residence],
        ]

        for row in infos:
            if y - row_height < 50:
                p.showPage()
                y = height - 350  # même ajustement sur les nouvelles pages

            x_pos = x_start
            max_cell_height = row_height
            cell_heights = []

            for i, cell in enumerate(row):
                texte = Paragraph(str(cell), styleN)
                w, h = texte.wrap(col_widths[i] - 2*padding_h, row_height - 2*padding_v)
                cell_heights.append(h + 2*padding_v)
            max_cell_height = max(max_cell_height, *cell_heights)

            for i, cell in enumerate(row):
                texte = Paragraph(str(cell), styleN)
                w, h = texte.wrap(col_widths[i] - 2*padding_h, max_cell_height - 2*padding_v)
                texte.drawOn(p, x_pos + padding_h, y - max_cell_height + padding_v)
                x_pos += col_widths[i]

            # Bordures
            x_pos = x_start
            for w in col_widths:
                p.rect(x_pos, y - max_cell_height, w, max_cell_height, stroke=1, fill=0)
                x_pos += w

            y -= max_cell_height

        p.showPage()

    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')


from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
def generer_pdf_structure_detail(request, pk):
    structure = get_object_or_404(Structure, pk=pk)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=50, leftMargin=50,
                            topMargin=100, bottomMargin=60)

    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH_centered = ParagraphStyle(
        name='Heading2Centered',
        parent=styles['Heading2'],
        alignment=TA_CENTER
    )

    elements = []

    # Titre général
    elements.append(Spacer(1, 200))
    elements.append(Paragraph("<b>Détails de la Structure</b>", styleH_centered ))
    elements.append(Spacer(1, 10))

    # Contenu du tableau
    def wrap_text(text, style=styleN):
        return Paragraph(str(text), style)

    infos = [
        [wrap_text('Attribut'), wrap_text('Valeur')],
        [wrap_text('Raison Sociale'), wrap_text(structure.raison_sociale)],
        [wrap_text('Date Création'), wrap_text(structure.date_creation.strftime('%d/%m/%Y %H:%M'))],
        [wrap_text('Adresse'), wrap_text(structure.adresse)],
        [wrap_text('Email'), wrap_text(structure.email)],
        [wrap_text('Téléphone'), wrap_text(structure.telephone)],
        [wrap_text('Pays'), wrap_text(structure.pays_residence)],
        [wrap_text('Devise du Pays'), wrap_text(structure.devise_pays)],
        [wrap_text('Direction de Tutelle'), wrap_text(structure.direction_tutelle)],
        [wrap_text('Structure sous Tutelle'), wrap_text(structure.structure_sous_tutelle)],
        [wrap_text('Matricule'), wrap_text(structure.matricule)],
        [wrap_text('Lieu de Résidence'), wrap_text(structure.lieu_residence)],
        [wrap_text('Logo Structure'), wrap_text(structure.logo_structure.url if structure.logo_structure else "N/A")],
        [wrap_text('Drapeau du Pays'), wrap_text(structure.drapeau_pays.url if structure.drapeau_pays else "N/A")],
    ]

    table = Table(infos, colWidths=[150, 350], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
    ]))

    elements.append(table)

    # Ajouter espace avant la fin
    elements.append(Spacer(1, 20))

    # Fonction pour canvas personnalisé (en-tête + pied)
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

                # En-tête sur la première page
                if i == 0:
                    generer_entete_structure_pdf(self, structure)

                # Pied sur la dernière page
                if i == total_pages - 1:
                    generer_pied_structure_pdf(self)

                # Numéro de page
                page_num_text = f"Page {i + 1} / {total_pages}"
                self.setFont("Times-Roman", 9)
                self.drawRightString(550, 20, page_num_text)

                super().showPage()
            super().save()

    # Générer le PDF
    doc.build(elements, canvasmaker=CustomCanvas)
    buffer.seek(0)
    return HttpResponse(buffer, content_type="application/pdf")
