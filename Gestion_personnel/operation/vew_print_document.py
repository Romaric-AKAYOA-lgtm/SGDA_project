from django.http import HttpResponse, Http404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
from reportlab.platypus import SimpleDocTemplate
from Gestion_personnel.operation.vew_print1 import generer_pied_structure_pdf
from reportlab.pdfgen import canvas as rcanvas
from referentiel.organisation_unite.models import OrganisationUnite
from referentiel.structure.models import Structure
from referentiel.structure.vew_impression import generer_entete_structure_pdf

from .models import Operation
from django.http import HttpResponse
from django.utils.timezone import now
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from io import BytesIO



from django.http import HttpResponse, Http404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY

from .models import Operation
from referentiel.structure.models import Structure



def generer_document_pdf(request, id_operation, type_doc, titre_pdf):
    try:
        operation = Operation.objects.get(id=id_operation)
    except Operation.DoesNotExist:
        raise Http404("Opération non trouvée.")

    # Structure
    structure = Structure.objects.first()
    if not structure:
        return HttpResponse("Structure introuvable", status=404)

    # Paragraphe justifié
    texte = generer_paragraphe_operation(id_operation, type_doc)

    # Préparer la réponse PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{titre_pdf}.pdf"'

    # Création canvas
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    x = 50
    y = generer_entete_structure_pdf(p, structure,operation.numero_fiche )
    y -= 25

    # Titre centré et souligné
    titre = titre_pdf.upper().replace('_', ' ')
    p.setFont("Times-Bold", 14)
    text_width = p.stringWidth(titre, "Times-Bold", 14)

    # Dessiner le titre
    p.drawCentredString(width / 2, y, titre)

    # Dessiner la ligne avec une marge (10 points plus bas que le texte)
    marge = 5
    p.line((width - text_width) / 2, y - marge, (width + text_width) / 2, y - marge)

    # Descendre le curseur pour le contenu suivant
    y -= 50


    # Style de paragraphe justifié
    style = ParagraphStyle(
        name='Justify',
        parent=getSampleStyleSheet()['Normal'],
        alignment=TA_JUSTIFY,
        fontName='Times-Roman',
        fontSize=14,
        leading=20
    )

    # Création et rendu du paragraphe
    para = Paragraph(texte, style)
    w, h = para.wrap(width - 100, height)
    para.drawOn(p, x, y - h)

    # Pied de page
    generer_pied_structure_pdf(p)

    p.showPage()
    p.save()
    return response



def certificat_prise_service(request, id_operation):
    return generer_document_pdf(request, id_operation, type_doc='certificat', titre_pdf='certificat de prise de service')


def attestation_prise_service(request, id_operation):
    return generer_document_pdf(request, id_operation, type_doc='attestation_prise', titre_pdf='attestation de prise de service')


def attestation_presence(request, id_operation):
    return generer_document_pdf(request, id_operation, type_doc='presence', titre_pdf='attestation de presence')


def attestation_employeur(request, id_operation):
    return generer_document_pdf(request, id_operation, type_doc='employeur', titre_pdf='attestation d employeur')


def attestation_cessation(request, id_operation):
    return generer_document_pdf(request, id_operation, type_doc='cessation', titre_pdf='attestation de cessation de service')

def generer_paragraphe_operation(id_operation, type_doc=None):
    try:
        operation = Operation.objects.select_related(
            'id_employe', 'id_fonction', 'id_organisation_unite'
        ).get(id=id_operation)
    except Operation.DoesNotExist:
        return "Opération introuvable."

    organisation = OrganisationUnite.objects.filter(organisation_unite_parent__isnull=True).first()
    if not organisation:
        return "Aucune organisation racine trouvée."

    employe = operation.id_employe
    fonction = operation.id_fonction.designation if operation.id_fonction else "Non précisé"
    unite = getattr(operation.id_organisation_unite, 'nom', str(operation.id_organisation_unite))

    date_debut = operation.date_debut.strftime("%d/%m/%Y") if operation.date_debut else "non précisée"
    heure_debut = operation.date_debut.strftime("%H:%M") if operation.date_debut else "00:00"
    date_creation = operation.date_creation.strftime("%d/%m/%Y") if operation.date_creation else "non précisée"
    date_fin = operation.date_fin.strftime("%d/%m/%Y") if operation.date_fin else "non précisée"
    heure_fin = operation.date_fin.strftime("%H:%M") if operation.date_fin else "00:00"
    type_operation = operation.type_operation

    # Gestion du type d'opération et du sexe
    if type_operation == "affectation":
        valeur_type = "affectée" if employe.sexe == "F" else "affecté"
    else:
        valeur_type = "mutée" if employe.sexe == "F" else "muté"

    if employe.sexe == "F":
        valeur_sexe = "inscrite"
        present = "présente"
        nomme = "nommée"
    else:
        valeur_sexe = "inscrit"
        present = "présent"
        nomme = "nommé"

    # Initialiser le texte par défaut
    texte = (
        f"La {organisation.designation} de l'{organisation.structure.raison_sociale}, soussignée, atteste que "
        f"Monsieur/Madame {employe.first_name} {employe.last_name},<br/><br/>"
        f"Grade : {employe.grade}, Échelon : {employe.echelle}, "
        f"Catégorie : {employe.categorie}, Matricule solde : {employe.matricule}, "
        f"{valeur_type} à l'{organisation.structure.raison_sociale} "
        f"par la note de service n° {operation.numero_note} du {date_creation}, "
    )

    # Gérer les différents types de documents
    if type_doc == 'certificat':
        texte += (
            f"a pris service le {date_debut} à {heure_debut} en qualité de {fonction} au service {unite}.<br/><br/>"
            f"En foi de quoi, le présent certificat lui est délivré pour servir et valoir ce que de droit."
        )

    elif type_doc == 'attestation_prise':
        texte += (
            f"a pris service le {date_debut} à {heure_debut} en qualité de {fonction}.<br/><br/>"
            f"En foi de quoi, la présente attestation lui est délivrée pour servir et valoir ce que de droit."
        )

    elif type_doc == 'presence':
        texte += (
            f"est {nomme} {fonction} par note de service et est régulièrement {present} à son poste de travail "
            f"par la note de service n° {operation.numero_note} du {date_creation}. "
            f"Il/Elle est bel et bien {present}(e) à son poste de travail "
            f"depuis le {date_debut} à {heure_debut}.<br/><br/>"
            f"Service {unite}.<br/><br/>"
            f"En foi de quoi, la présente attestation lui est délivrée pour servir et valoir ce que de droit."
        )

    elif type_doc == 'employeur':
        texte = (
            f"La {organisation.designation} de l'{organisation.structure.raison_sociale}, soussignée, atteste que "
            f"Monsieur/Madame {employe.first_name} {employe.last_name}, matricule solde : {employe.matricule}, "
            f"Grade : {employe.grade},<br/><br/>"
            f"est bel et bien {valeur_sexe} dans l'effectif de l'enseignement de "
            f"l'{organisation.structure.raison_sociale}.<br/><br/>"
            f"En qualité de {fonction}, depuis le {date_debut} à {heure_debut}.<br/><br/>"
            f"En foi de quoi, la présente attestation lui est délivrée pour servir et valoir ce que de droit."
        )

    elif type_doc == 'cessation':
        texte = (
            f"La {organisation.designation} de l'{organisation.structure.raison_sociale}, soussignée, atteste que "
            f"Monsieur/Madame {employe.first_name} {employe.last_name},<br/><br/>"
            f"Matricule solde : {employe.matricule}, Grade : {employe.grade}, "
            f"fonction : {fonction} au sein de l'{organisation.structure.raison_sociale}, "
            f"cesse définitivement ses fonctions le {date_fin} à {heure_fin}.<br/><br/>"
            f"En foi de quoi, la présente attestation lui est délivrée pour servir et valoir ce que de droit."
        )

    else:
        texte = "Type de document non reconnu."

    # Mise en majuscule automatique après chaque point final
    import re
    texte = re.sub(
        r"([.!?])(\s*)([a-zàâçéèêëîïôûùüÿñæœ])",
        lambda m: m.group(1) + m.group(2) + m.group(3).upper(),
        texte
    )

    return texte

def _build_operations_pdf(operations, titre_pdf, request):
    structure = Structure.objects.first()
    if not structure:
        return HttpResponse("Structure introuvable", status=404)

    elements = []
    elements.append(Spacer(1, 40))
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title', parent=styles['Title'],
        fontName='Times-Bold', fontSize=20,
        alignment=1, spaceAfter=20
    )
    header_style = ParagraphStyle('Header', fontName='Times-Bold', fontSize=10, alignment=1)
    cell_style = ParagraphStyle('Cell', fontName='Times-Roman', fontSize=9)

    headers = ["N° Fiche", "Type", "Employé", "Fonction", "Début", "Fin", "Statut"]
    count = operations.count()

    # Construire les lignes du tableau
    all_rows = []
    for op in operations:
        all_rows.append([
            Paragraph(str(op.numero_fiche), cell_style),
            Paragraph(op.get_type_operation_display(), cell_style),
            Paragraph(f"{op.id_employe.last_name} {op.id_employe.first_name}", cell_style),
            Paragraph(op.id_fonction.designation, cell_style),
            Paragraph(op.date_debut.strftime('%d/%m/%Y'), cell_style),
            Paragraph(op.date_fin.strftime('%d/%m/%Y') if op.date_fin else '', cell_style),
            Paragraph(op.get_statut_display(), cell_style),
        ])

    # Construire le tableau complet
    data = [[Paragraph(h, header_style) for h in headers]] + all_rows
    table = Table(data, colWidths=[50, 60, 100, 100, 60, 60, 60], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    # Ajouter le titre, le tableau et le total
    elements.append(Spacer(1, 230))
    elements.append(Paragraph(f"<u>{titre_pdf}</u>", title_style))
    elements.append(Spacer(1, 20))
    elements.append(table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Nombre total d'opérations : {count}", cell_style))
    elements.append(Spacer(1, 10))

    # Création PDF
    final_buffer = BytesIO()

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

    # Création du document
    doc = SimpleDocTemplate(
        final_buffer,
        pagesize=A4,
        topMargin=50,
        leftMargin=50,
        rightMargin=50,
        bottomMargin=50,
    )
    doc.build(elements, canvasmaker=CustomCanvas)

    # Réponse HTTP
    response = HttpResponse(final_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{titre_pdf}.pdf"'
    return response




# Vues pour urls.py
def imprimer_toutes_operations(request):
    operations = Operation.objects.all().order_by('date_creation')
    return _build_operations_pdf(operations, "Toutes les opérations", request)

def imprimer_operations_mois(request):
    today = now()
    operations = Operation.objects.filter(date_creation__year=today.year, date_creation__month=today.month).order_by('date_creation')
    return _build_operations_pdf(operations, f"Opérations du mois {today.strftime('%m/%Y')}", request)

def imprimer_operations_annee(request):
    today = now()
    operations = Operation.objects.filter(date_creation__year=today.year).order_by('date_creation')
    return _build_operations_pdf(operations, f"Opérations de l'année {today.year}", request)
