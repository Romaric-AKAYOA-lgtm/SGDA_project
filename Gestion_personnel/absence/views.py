from datetime import datetime
from io import BytesIO
from django.utils.timezone import now
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from collections import defaultdict
from datetime import datetime
from django.db.models import Max
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Case, When, Value, IntegerField, Max
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
from django.http import HttpResponse
import io, zipfile
from xhtml2pdf import pisa
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas as rcanvas
from .models import Operation, Absence
from .forms import AbsenceForm
from referentiel.structure.models import Structure
from referentiel.structure.vew_impression import generer_entete_structure_pdf
from Gestion_personnel.operation.views import generer_pied_structure_pdf



# ✅ Liste des absences avec recherche et pagination, sans filtre sur le statut

def absence_list(request):
    query = request.GET.get('q', '').strip()
    current_year = timezone.now().year  # Obtenir l'année en cours

    absences_qs = Absence.objects.select_related(
        "id_absence_operation_employe__id_employe"
    ).filter(date_creation__year=current_year)

    if query:
        filters = (
            Q(lieu__icontains=query) |
            Q(motif__icontains=query) |
            Q(numero_note__icontains=query) |
            Q(numero_fiche__icontains=query) |
            Q(statut__icontains=query) |
            Q(type_absence__icontains=query) |
            Q(id_absence_operation_employe__id_employe__matricule__icontains=query) |
            Q(id_absence_operation_employe__id_employe__last_name__icontains=query) |
            Q(id_absence_operation_employe__id_employe__first_name__icontains=query)
        )

        # Essayer de convertir la recherche en date au format JJ/MM/AAAA
        try:
            search_date = datetime.strptime(query, "%d/%m/%Y").date()
        except ValueError:
            search_date = None

        if search_date:
            filters |= (
                Q(date_creation__date=search_date) |
                Q(date_debut__date=search_date) |
                Q(date_retour__date=search_date) |
                Q(date_retour_effective__date=search_date)
            )

        absences_qs = absences_qs.filter(filters)

    absences_qs = absences_qs.order_by('-date_creation')

    paginator = Paginator(absences_qs, 10)
    page_number = request.GET.get('page')
    absences = paginator.get_page(page_number)

    return render(request, 'absence/absence_list.html', {
        'absences': absences,
        'search_query': query,
    })

# ✅ Création d'une absence
def absence_create(request):
    form = AbsenceForm(request.POST or None, request=request)  # <-- passer request

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Absence enregistrée avec succès.")
            if request.POST.get("action") == "save_and_new":
                return redirect('absence:ajouter')
            return redirect('absence:liste')
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")

    return render(request, 'absence/absence_form.html', {
        'form': form,
        'mode': 'ajouter',
    })


# ✅ Modification d'une absence
def absence_update(request, pk):
    absence = get_object_or_404(Absence, pk=pk)
    form = AbsenceForm(request.POST or None, instance=absence, request=request)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Absence mise à jour avec succès.")
            return redirect('absence:liste')
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")

    return render(request, 'absence/absence_form.html', {
        'form': form,
        'mode': 'modifier',
        'absence': absence,
    })


# ✅ Recherche avancée des absences
def absence_search(request):
    query = request.GET.get('q', '').strip()

    absences_qs = Absence.objects.select_related(
        "id_absence_operation_employe__id_employe"
    ).all().order_by('date_creation')

    if query:
        filters = (
            Q(lieu__icontains=query) |
            Q(motif__icontains=query) |
            Q(numero_note__icontains=query) |
            Q(numero_fiche__icontains=query) |
            Q(statut__icontains=query) |
            Q(type_absence__icontains=query) |
            Q(id_absence_operation_employe__id_employe__matricule__icontains=query) |
            Q(id_absence_operation_employe__id_employe__last_name__icontains=query) |
            Q(id_absence_operation_employe__id_employe__first_name__icontains=query)
        )

        # Essayer de convertir la recherche en date au format JJ/MM/AAAA
        try:
            search_date = datetime.strptime(query, "%d/%m/%Y").date()
        except ValueError:
            search_date = None

        if search_date:
            filters |= (
                Q(date_creation__date=search_date) |
                Q(date_debut__date=search_date) |
                Q(date_retour__date=search_date) |
                Q(date_retour_effective__date=search_date)
            )

        absences_qs = absences_qs.filter(filters)

    # Annoter pour mettre les absences "confirmées" en premier
    absences_qs = absences_qs.annotate(
        statut_priority=Case(
            When(statut='confirme', then=Value(0)),
            default=Value(1),
            output_field=IntegerField()
        )
    ).order_by('statut_priority', '-date_creation')

    paginator = Paginator(absences_qs, 10)
    page_number = request.GET.get('page')
    absences = paginator.get_page(page_number)

    return render(request, 'absence/absence_search.html', {
        'absences': absences,
        'query': query,
    })



# ✅ Génération PDF utilitaire
def render_to_pdf(template_src, context_dict):
    html = render_to_string(template_src, context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse("Erreur lors de la génération du PDF", status=500)



def generer_paragraphe_absence(id_absence):
    absence = get_object_or_404(Absence, id=id_absence)
    employe = absence.id_absence_operation_employe.id_employe
    type_abs = absence.get_type_absence_display()
    lieu = absence.lieu
    date_debut = absence.date_debut.strftime("%d/%m/%Y")
    date_retour = absence.date_retour.strftime("%d/%m/%Y")
    motif = absence.motif or "Non précisé"

    return (
        f"{employe.first_name} {employe.last_name} est autorisé(e) à s’absenter pour : {type_abs}. "
        f"L'absence se déroulera du {date_debut} au {date_retour}, au lieu de {lieu}. "
        f"Motif : {motif}."
    )

def generer_pdf_absence(request, id_absence):

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Récupérer la première structure (par exemple)
    structure = Structure.objects.first()
    # Exemple : générer l'en-tête avec la structure
    y = generer_entete_structure_pdf(p, structure)  # tu peux adapter ta fonction pour prendre structure en paramètre
    y -= 20

    paragraphe = generer_paragraphe_absence(id_absence)

    p.setFont("Times-Roman", 12)
    lines = simpleSplit(paragraphe, "Times-Roman", 12, width - 100)
    for line in lines:
        if y < 100:
            p.showPage()
            p.setFont("Times-Roman", 12)
            y = height - 100
        p.drawString(50, y, line)
        y -= 20

    absence = get_object_or_404(Absence, id=id_absence)
    absence_emp_nom = absence.id_absence_operation_employe.id_employe.last_name
    absence_emp_prenom = absence.id_absence_operation_employe.id_employe.first_name
    absence_emp_fullname = f"{absence_emp_nom}_{absence_emp_prenom}"
    generer_pied_structure_pdf(p)

    p.showPage()
    p.save()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="absence_{absence_emp_fullname}.pdf"'

    return response

def generer_paragraphe_absence_operation(id_absence, type_doc=None):
    absence = get_object_or_404(Absence, id=id_absence)
    operation =absence 


    organisation=operation.id_absence_operation_employe.id_fonction.structure.raison_sociale
    organisation_unit=operation.id_absence_operation_employe.id_organisation_unite.designation
    employe = operation.id_absence_operation_employe.id_employe
    fonction = operation.id_absence_operation_employe.id_fonction.designation if operation.id_absence_operation_employe.id_fonction.designation else "fonction inconnue"
    unite = getattr(operation.id_absence_operation_employe.id_organisation_unite, 'nom', str(operation.id_absence_operation_employe.id_organisation_unite))
    annee_debut = operation.date_debut.strftime("%Y") if operation.date_debut else "année non précisée"

    date_debut = operation.date_debut.strftime("%d/%m/%Y") if operation.date_debut else "date non précisée"
    heure_debut = operation.date_debut.strftime("%H:%M") if operation.date_debut else ""
    dure= operation.duree
    date_creation = operation.date_creation.strftime("%d/%m/%Y") if operation.date_creation else "non précisée"
    date_fin_pr = operation.date_retour.strftime("%d/%m/%Y") if operation.date_retour else "non précisée"
    heure_fin_pr = operation.date_retour.strftime("%H:%M") if operation.date_retour else ""
  
    date_fin = operation.date_retour_effective.strftime("%d/%m/%Y") if operation.date_retour_effective else "non précisée"
    heure_retour_effective = operation.date_retour_effective.strftime("%H:%M") if operation.date_retour_effective else ""
    texte = (
        f"La {organisation_unit} de l'{organisation}, soussignée, atteste que "
        f"Monsieur/Madame {employe.first_name} {employe.last_name}.\n\n"

    )

    if type_doc in ['certificat', 'attestation_prise']:
        texte += (
            f"Grade : {employe.grade}, Échelon : {employe.echelle}, Catégorie : {employe.categorie}, "
            f"Matricule solde : {employe.matricule}, en service à l'{organisation}, "
            f"de retour de congé, autorisé par l'attestation ou note de service n° {operation.numero_note}  "
            f" du {date_creation}."
            f" a repris service le {date_fin} à {heure_retour_effective}.\n\n"
            f"En foi de quoi, le présent certificat lui est délivré pour servir et valoir ce que de droit."
        )

    elif type_doc == 'presence':
        texte += (
            f"Matricule : {employe.matricule}, Grade : {employe.grade}, Fonction : {fonction}, "
            f"service : {organisation_unit}, est autorisé(e) à s’absenter de son poste de travail "
            f"du {date_debut} au {date_fin_pr}, afin de se rendre à {absence.lieu} pour le motif suivant : {absence.motif}.\n\n"
            f"En foi de quoi, la présente autorisation lui est délivrée pour servir et valoir ce que de droit."
        )


    elif type_doc == 'employeur':
        texte += (
              f"\n\nIl/Elle travaille comme {fonction} dans l’unité {unite} depuis le {date_debut} à {heure_debut}.\n\n"
            f"Attestation délivrée pour servir et valoir ce que de droit."
        )

    elif type_doc == 'cessation':
        texte += (
           f"Matricule : {employe.matricule}, Grade : {employe.grade}, Fonction : {fonction},  en service à l'{organisation}, bénéficie d'un cogé administratif de  {dure} mois  au titre de l'année  {annee_debut}, accordé par l'autorisation /note de service n° {operation.numero_note} "
            f"du {date_creation}, a effectiviement cessé le travail le {date_debut} à {heure_debut} heures précises.. L'intéressé (e) reprendra ses activités, le  {date_fin_pr} à  {heure_fin_pr} \n\n"
            f"En foi de quoi, la présente autorisation lui est délivrée pour servir et valoir ce que de droit."
        )
    else:
        texte += (
            f"\n\n**ERREUR :**\n\n"
            f"Type de document non reconnu."
        )

    return texte



# Pour compatibilité, on peut aussi garder les fonctions d'appel spécifiques (facultatif)
def generer_paragraphe_certificat_reprise(id_absence):
    return generer_paragraphe_absence_operation(id_absence, type_doc='certificat')

def generer_paragraphe_attestation_presence(id_absence):
    return generer_paragraphe_absence_operation(id_absence, type_doc='presence')

def generer_paragraphe_attestation_cessation(id_absence):
    return generer_paragraphe_absence_operation(id_absence, type_doc='cessation')

def generer_paragraphe_attestation_employeur(id_absence):
    return generer_paragraphe_absence_operation(id_absence, type_doc='employeur')
def  generer_paragraphe_calendrier_conge():
      return generer_paragraphe_absence_operation( type_doc='calendrier')

def generer_pdf_template(request, id_absence, paragraphe_func, nom_fichier, titre_document):
    width, height = A4
    marge_gauche = 50
    marge_droite = 50
    marge_haut = 100
    marge_bas = 100
    largeur_texte = width - marge_gauche - marge_droite

    absence = get_object_or_404(Absence, id=id_absence)
    absence_emp_nom = absence.id_absence_operation_employe.id_employe.last_name
    absence_emp_prenom = absence.id_absence_operation_employe.id_employe.first_name
    absence_emp_fullname = f"{absence_emp_nom} {absence_emp_prenom}"
    structure = Structure.objects.first()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{nom_fichier}_{absence_emp_fullname}.pdf"'
    p = canvas.Canvas(response, pagesize=A4)

    y = height - marge_haut  # initialisation de y

    def dessiner_entete_titre():
        nonlocal y
        y = generer_entete_structure_pdf(p, structure, absence.numero_note)  # entête personnalisée
        y -= 20
        p.setFont("Times-Bold", 16)
        p.drawCentredString(width / 2, y, titre_document.upper())
        text_width = p.stringWidth(titre_document.upper(), "Times-Bold", 16)
        x_start = (width / 2) - (text_width / 2)
        x_end = (width / 2) + (text_width / 2)
        p.setLineWidth(1)
        p.line(x_start, y - 2, x_end, y - 2)
        y -= 60

    def dessiner_pied():
        generer_pied_structure_pdf(p)  # ta fonction pied personnalisée

    def drawJustifiedLine(text, x, y, max_width):
        mots = text.split()
        if len(mots) == 1:
            p.drawString(x, y, text)
            return
        largeur_texte = sum([p.stringWidth(mot, "Times-Roman", 14) for mot in mots])
        espace_total = max_width - largeur_texte
        nb_espaces = len(mots) - 1
        espace_par_espace = espace_total / nb_espaces if nb_espaces > 0 else 0
        current_x = x
        for i, mot in enumerate(mots):
            p.drawString(current_x, y, mot)
            largeur_mot = p.stringWidth(mot, "Times-Roman", 14)
            current_x += largeur_mot
            if i < nb_espaces:
                current_x += espace_par_espace

    # Initialisation
    dessiner_entete_titre()

    paragraphe = paragraphe_func(id_absence)
    p.setFont("Times-Roman", 14)
    leading = int(14 * 1.5)  # interligne 1.5

    paragraphes = paragraphe.split('\n\n')
    for parag in paragraphes:
        lines = simpleSplit(parag, "Times-Roman", 14, largeur_texte)
        for i, line in enumerate(lines):
            if y < marge_bas:
                dessiner_pied()
                p.showPage()
                dessiner_entete_titre()
                p.setFont("Times-Roman", 14)

            if i == len(lines) - 1:
                p.drawString(marge_gauche, y, line)
            else:
                drawJustifiedLine(line, marge_gauche, y, largeur_texte)
            y -= leading
        y -= leading  # espace entre paragraphes

    dessiner_pied()
    p.showPage()
    p.save()

    return response


def generer_pdf_absence(request, id_absence):
    # Ici, on garde la version simple si besoin (optionnel)
    absence = get_object_or_404(Absence, id=id_absence)
    paragraphe = (
        f"{absence.id_absence_operation_employe.id_employe.first_name} "
        f"{absence.id_absence_operation_employe.id_employe.last_name} est autorisé(e) à s’absenter."
    )
    # Ou utiliser generer_paragraphe_absence directement

    return generer_pdf_template(
        request,
        id_absence,
        generer_paragraphe_absence,
        "absence",
        "Attestation d'Absence"
    )

def certificat_reprise_service(request, id_absence):
    return generer_pdf_template(
        request,
        id_absence,
        generer_paragraphe_certificat_reprise,
        "certificat_reprise_service",
        "Certificat de Reprise de Service"
    )

def attestation_cessation_service(request, id_absence):
    return generer_pdf_template(
        request,
        id_absence,
        generer_paragraphe_attestation_cessation,
        "attestation_cessation_service",
        "Attestation de Cessation de Service"
    )

def attestation_presence(request, id_absence):
    return generer_pdf_template(
        request,
        id_absence,
        generer_paragraphe_attestation_presence,
        "attestation_presence",
        "Attestation d'absence"
    )

def attestation_employeur(request, id_absence):
    return generer_pdf_template(
        request,
        id_absence,
        generer_paragraphe_attestation_employeur,
        "attestation_employeur",
        "Attestation Employeur"
    )


def imprimer_toutes_les_absences(request):
    return generer_pdf_template_tableau(
        request,
        generer_lignes_par_service,
        "calendrier_conge",
        "Calendrier des congés"
    )


def generer_pdf_template_tableau(request, lignes_func, nom_fichier, titre_document, id_absence=None):
    # --- Configuration de la réponse HTTP ---
    response = HttpResponse(content_type='application/pdf')
    filename = f'{nom_fichier}_{id_absence}.pdf' if id_absence else f'{nom_fichier}.pdf'
    response['Content-Disposition'] = f'inline; filename="{filename}"'

    styles = getSampleStyleSheet()
    structure = Structure.objects.first()
    annee = datetime.now().year

    # --- Canvas personnalisé pour en-tête et pied ---

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

    # --- Définir le cadre de contenu principal ---
    frame = Frame(
        40, 60,  # x, y
        A4[0] - 80,  # largeur utile
        A4[1] - 120,  # hauteur utile
        id='normal'
    )

    # --- PageTemplate minimal pour BaseDocTemplate ---
    def on_page(canvas, doc):
        pass  # le canvas sera géré par CustomCanvas, donc ici rien à faire

    template = PageTemplate(id='main', frames=[frame], onPage=on_page)
    doc = BaseDocTemplate(
        response,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=60,
        bottomMargin=40,
        pageTemplates=[template]
    )

    # --- Contenu du document ---
    elements = []

    # Titre principal
    titre_complet = f"{titre_document} annuel de l'année {annee}"
    elements.append(Spacer(1, 250))
    elements.append(Paragraph(f"<b><font size=16>{titre_complet.upper()}</font></b>", styles['Title']))
    elements.append(Spacer(1, 20))

    # Récupération des blocs de données
    blocs = lignes_func()
    col_widths = [80, 80, 100, 200]

    for service, lignes in blocs.items():
        elements.append(Paragraph(f"<b><font size=14>Service : {service}</font></b>", styles['Heading3']))
        elements.append(Spacer(1, 12))

        table = Table(lignes, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

    # --- Générer le PDF avec CustomCanvas ---
    doc.build(elements, canvasmaker=CustomCanvas)
    return response


def generer_lignes_par_service():
    blocs = defaultdict(list)
    en_tete = ["Nom", "Prénom", "Mois souhaité", "Lieu"]

    styles = getSampleStyleSheet()
    wrap_style = ParagraphStyle(
        'wrap_style',
        parent=styles['Normal'],
        wordWrap='CJK',
        fontSize=10,
        leading=12
    )

    # Récupérer la date_debut la plus récente par employé
    dernieres_dates = Operation.objects.values('id_employe').annotate(dernier_debut=Max('date_debut'))

    # Puis récupérer les opérations correspondant à ces dates (une opération par employé)
    operations = Operation.objects.filter(
        id_employe__in=[d['id_employe'] for d in dernieres_dates],
        date_debut__in=[d['dernier_debut'] for d in dernieres_dates]
    )

    for op in operations:
        employe = op.id_employe
        service = op.id_organisation_unite.designation if op.id_organisation_unite else "Non précisé"
        nom = employe.last_name if employe else "Non précisé"
        prenom = employe.first_name if employe else "Non précisé"

        ligne = [
            Paragraph(nom, wrap_style),
            Paragraph(prenom, wrap_style),
            Paragraph("", wrap_style),  # Mois souhaité vide
            Paragraph("", wrap_style)   # Lieu vide
        ]

        if not blocs[service]:
            blocs[service].append(en_tete)
        blocs[service].append(ligne)

    return blocs


def generer_pdf_conges_annuels(request):
    current_year = now().year

    conges_annuels = Absence.objects.filter(
        type_absence="conge_annuel",
        date_debut__year=current_year
    ).order_by("id_absence_operation_employe", "date_debut")

    if not conges_annuels:
        return HttpResponse("Aucun congé annuel trouvé pour cette année.")

    # Créer un buffer mémoire pour le ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for conge in conges_annuels:
            absence_emp_nom = conge.id_absence_operation_employe.id_employe.last_name
            absence_emp_prenom = conge.id_absence_operation_employe.id_employe.first_name
            absence_emp_fullname = f"{absence_emp_nom}_{absence_emp_prenom}"
            # Générer le PDF pour ce congé
            pdf_response = attestation_cessation_service(request, conge.id)
            # Lire le contenu PDF en bytes
            pdf_bytes = pdf_response.content
            
            # Nommer chaque PDF avec le matricule ou l'ID
            nom_pdf = f"attestation_conge_{absence_emp_fullname}.pdf"
            
            # Ajouter au ZIP
            zip_file.writestr(nom_pdf, pdf_bytes)

    # Retourner le ZIP
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type="application/zip")
    response['Content-Disposition'] = f'attachment; filename="attestations_conges_annuels.zip"'
    return response


