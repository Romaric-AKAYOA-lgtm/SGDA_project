from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas as rcanvas
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse

from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

from Gestion_personnel.operation.vew_print1 import generer_pied_structure_pdf
from referentiel.structure.models import Structure
from referentiel.structure.vew_impression import generer_entete_structure_pdf

from .forms import PriseEnChargeAdherentForm
from .models import PriseEnChargeAdherent

# Liste des prises en charge
def prise_en_charge_list(request):
    query = request.GET.get('q', '').strip()
    prises = PriseEnChargeAdherent.objects.all().order_by('-date_creation')
    
    if query:
        prises = prises.filter(
            Q(objet__icontains=query) |
            Q(description__icontains=query) |
            Q(nom_complet_medecin__icontains=query) |
            Q(fonction_medecin__icontains=query) |
            Q(specialite_medecin__icontains=query)
        ).order_by("-date_creation")
    paginator = Paginator(prises, 10)
    page_number = request.GET.get('page')
    prises = paginator.get_page(page_number)
    return render(request, 'Prise_en_charge_adherent/prise_en_charge_list.html', {
        'prises': prises,
        'query': query
    })

# ===============================
#  Création
# ===============================
def prise_en_charge_create(request):
    form = PriseEnChargeAdherentForm(request.POST or None, request=request)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Prise en charge enregistrée avec succès.")
            
            # Si on clique sur "Enregistrer et Nouveau"
            if request.POST.get('action') == 'save_and_new':
                return redirect('prise_en_charge:create')
            
            # Sinon on retourne à la liste
            return redirect('prise_en_charge:list')
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")

    return render(request, 'Prise_en_charge_adherent/prise_en_charge_form.html', {
        'form': form,
        'mode': 'ajouter'
    })


# ===============================
#  Modification
# ===============================
def prise_en_charge_update(request, pk):
    prise = get_object_or_404(PriseEnChargeAdherent, pk=pk)
    form = PriseEnChargeAdherentForm(request.POST or None, instance=prise, request=request)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Prise en charge mise à jour avec succès.")
            return redirect('prise_en_charge:list')
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")

    return render(request, 'Prise_en_charge_adherent/prise_en_charge_form.html', {
        'form': form,
        'mode': 'modifier',
        'prise': prise
    })


# Détail
def prise_en_charge_detail(request, pk):
    prise = get_object_or_404(PriseEnChargeAdherent, pk=pk)
    return render(request, 'Prise_en_charge_adherent/prise_en_charge_detail.html', {
        'prise': prise
    })

# Suppression
def prise_en_charge_delete(request, pk):
    prise = get_object_or_404(PriseEnChargeAdherent, pk=pk)
    prise.delete()
    messages.success(request, "Prise en charge supprimée avec succès.")
    return redirect('prise_en_charge:list')

# Impression liste
def prise_en_charge_print_list(request):
    prises = PriseEnChargeAdherent.objects.all().order_by('-date_creation')
    return render(request, 'Prise_en_charge_adherent/prise_en_charge_print_list.html', {
        'prises': prises
    })

# Impression détail
def prise_en_charge_print_detail(request, pk):
    prise = get_object_or_404(PriseEnChargeAdherent, pk=pk)
    return render(request, 'Prise_en_charge_adherent/prise_en_charge_print_detail.html', {
        'prise': prise
    })


def prise_en_charge_print_list(request):
    structure = Structure.objects.first()  # entête si disponible

    # Date système pour filtrer
    now = datetime.now()
    annee = now.year
    mois = now.month

    # Filtrer les prises en charge de l'année et mois en cours
    prises = PriseEnChargeAdherent.objects.filter(
        date_creation__year=annee,
        #date_creation__month=mois
    ).order_by('-date_creation')

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=50,
        leftMargin=50,
        rightMargin=50,
        bottomMargin=50,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Title', parent=styles['Title'], fontName='Times-Bold', fontSize=16)
    cell_style = ParagraphStyle(name='Cell', parent=styles['Normal'], fontName='Times-Roman', fontSize=12)

    elements = []
    elements.append(Spacer(1, 250))
    elements.append(Paragraph("Liste des prises en charge (Mois courant)", title_style))
    elements.append(Spacer(1, 20))

    for prise in prises:
        adherent = prise.adherent
        data = [
            [Paragraph("Nom complet", cell_style), Paragraph(f"{adherent.last_name} {adherent.first_name}", cell_style)],
            [Paragraph("Date de naissance", cell_style), Paragraph(adherent.date_naissance.strftime('%d/%m/%Y') if adherent.date_naissance else '', cell_style)],
            [Paragraph("Âge", cell_style), Paragraph(str(adherent.calculate_age(adherent.date_naissance)) if adherent.date_naissance else '', cell_style)],
            [Paragraph("Sexe", cell_style), Paragraph(adherent.sexe or '', cell_style)],
            [Paragraph("Téléphone", cell_style), Paragraph(adherent.telephone or '', cell_style)],
            [Paragraph("Champ", cell_style), Paragraph("Valeur", cell_style)],
            [Paragraph("Objet", cell_style), Paragraph(prise.objet, cell_style)],
            [Paragraph("Description", cell_style), Paragraph(prise.description or '', cell_style)],
            [Paragraph("Date de création", cell_style), Paragraph(prise.date_creation.strftime('%d/%m/%Y %H:%M'), cell_style)],
            [Paragraph("Nom médecin", cell_style), Paragraph(prise.nom_complet_medecin or '', cell_style)],
            [Paragraph("Fonction médecin", cell_style), Paragraph(prise.fonction_medecin or '', cell_style)],
            [Paragraph("Spécialité médecin", cell_style), Paragraph(prise.specialite_medecin or '', cell_style)],
            [Paragraph("Opération enregistrée", cell_style), Paragraph(str(prise.operation_enregistrer), cell_style)],
            [Paragraph("Opération médecin", cell_style), Paragraph(str(prise.operation_medecin) if prise.operation_medecin else '', cell_style)],
        ]

        table = Table(data, colWidths=[150, 300])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

    # Canvas personnalisé pour entête et pied de page

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

    # Construction finale du PDF
    doc.build(elements, canvasmaker=CustomCanvas)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="liste_prises_en_charge.pdf"'
    return response


# === Détail d'une prise en charge ===
def prise_en_charge_print_detail(request, pk):
    prise = get_object_or_404(PriseEnChargeAdherent, pk=pk)
    structure = Structure.objects.first()  # Pour l'en-tête

    # Styles PDF
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name='Title',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=16
    )
    cell_style = ParagraphStyle(
        name='Cell',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12
    )

    # Contenu PDF
    elements = []
    elements.append(Spacer(1, 250))
    elements.append(Paragraph(
        f"Prise en charge : {prise.objet} du {prise.date_creation.strftime('%d/%m/%Y')}",
        title_style
    ))
    elements.append(Spacer(1, 20))

    adherent = prise.adherent
    data = [
        [Paragraph("Nom complet", cell_style), Paragraph(f"{adherent.last_name} {adherent.first_name}", cell_style)],
        [Paragraph("Date de naissance", cell_style), Paragraph(adherent.date_naissance.strftime('%d/%m/%Y') if adherent.date_naissance else '', cell_style)],
        [Paragraph("Âge", cell_style), Paragraph(str(adherent.calculate_age(adherent.date_naissance)) if adherent.date_naissance else '', cell_style)],
        [Paragraph("Sexe", cell_style), Paragraph(adherent.sexe or '', cell_style)],
        [Paragraph("Téléphone", cell_style), Paragraph(adherent.telephone or '', cell_style)],
        [Paragraph("Objet", cell_style), Paragraph(prise.objet, cell_style)],
        [Paragraph("Description", cell_style), Paragraph(prise.description or '', cell_style)],
        [Paragraph("Date de création", cell_style), Paragraph(prise.date_creation.strftime('%d/%m/%Y %H:%M'), cell_style)],
        [Paragraph("Nom médecin", cell_style), Paragraph(prise.nom_complet_medecin or '', cell_style)],
        [Paragraph("Fonction médecin", cell_style), Paragraph(prise.fonction_medecin or '', cell_style)],
        [Paragraph("Spécialité médecin", cell_style), Paragraph(prise.specialite_medecin or '', cell_style)],
        [Paragraph("Opération enregistrée", cell_style), Paragraph(str(prise.operation_enregistrer), cell_style)],
        [Paragraph("Opération médecin", cell_style), Paragraph(str(prise.operation_medecin) if prise.operation_medecin else '', cell_style)],
    ]

    table = Table(data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table)

    # HTML si demandé
    if request.GET.get('format') == 'html':
        return render(request, 'Prise_en_charge_adherent/prise_en_charge_print_detail.html', {'prise': prise})

    # Génération PDF
    buffer = BytesIO()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="prise_en_charge_{pk}.pdf"'

    # Canvas personnalisé pour gérer en-tête, pied et pagination
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

    # Création du document PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=50,
        leftMargin=50,
        rightMargin=50,
        bottomMargin=50
    )

    doc.build(elements, canvasmaker=CustomCanvas)
    buffer.seek(0)
    response.write(buffer.read())
    return response


def adherent_prises_en_charge_print_pdf(adherent):
    """
    Retourne une liste de Flowables représentant les prises en charge
    pour un adhérent donné. Ne crée pas de page si aucune prise en charge.
    """
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name='Title',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=16
    )
    cell_style = ParagraphStyle(
        name='Cell',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12
    )
    prises = PriseEnChargeAdherent.objects.filter(adherent=adherent).order_by('-date_creation')
    elements = []

    if prises.exists():
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(name='Title', parent=styles['Title'], fontName='Times-Bold', fontSize=14)
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Prises en charge de l'adhérent", title_style))
        elements.append(Spacer(1, 20))

        for prise in prises:
            adherent = prise.adherent
            data = [
                [Paragraph("Nom complet", cell_style), Paragraph(f"{adherent.last_name} {adherent.first_name}", cell_style)],
                [Paragraph("Date de naissance", cell_style), Paragraph(adherent.date_naissance.strftime('%d/%m/%Y') if adherent.date_naissance else '', cell_style)],
                [Paragraph("Âge", cell_style), Paragraph(str(adherent.calculate_age(adherent.date_naissance)) if adherent.date_naissance else '', cell_style)],
                [Paragraph("Sexe", cell_style), Paragraph(adherent.sexe or '', cell_style)],
                [Paragraph("Téléphone", cell_style), Paragraph(adherent.telephone or '', cell_style)],
                [Paragraph("Objet", cell_style), Paragraph(prise.objet, cell_style)],
                [Paragraph("Description", cell_style), Paragraph(prise.description or '', cell_style)],
                [Paragraph("Date de création", cell_style), Paragraph(prise.date_creation.strftime('%d/%m/%Y %H:%M'), cell_style)],
                [Paragraph("Nom médecin", cell_style), Paragraph(prise.nom_complet_medecin or '', cell_style)],
                [Paragraph("Fonction médecin", cell_style), Paragraph(prise.fonction_medecin or '', cell_style)],
                [Paragraph("Spécialité médecin", cell_style), Paragraph(prise.specialite_medecin or '', cell_style)],
                [Paragraph("Opération enregistrée", cell_style), Paragraph(str(prise.operation_enregistrer), cell_style)],
                [Paragraph("Opération médecin", cell_style), Paragraph(str(prise.operation_medecin) if prise.operation_medecin else '', cell_style)],
            ]

            table = Table(data, colWidths=[150, 300])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 40))

    # Toujours retourner une liste, même vide, pour compatibilité avec la fusion PDF
    return elements
