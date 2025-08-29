from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import PriseEnChargeAdherent
from .forms import PriseEnChargeAdherentForm
from django.shortcuts import get_object_or_404, render
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

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
        )
    
    return render(request, 'Prise_en_charge_adherent/prise_en_charge_list.html', {
        'prises': prises,
        'query': query
    })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import PriseEnChargeAdherent
from .forms import PriseEnChargeAdherentForm


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


# === Liste de prises en charge ===

def prise_en_charge_print_list(request):
    prises = PriseEnChargeAdherent.objects.all().order_by('-date_creation')

    # Vérifier si on veut un rendu HTML
    if request.GET.get('format') == 'html':
        return render(request, 'Prise_en_charge_adherent/prise_en_charge_print_list.html', {
            'prises': prises
        })

    # Préparation Flowables pour PDF
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Title', parent=styles['Title'], fontName='Times-Bold', fontSize=16)
    cell_style = ParagraphStyle(name='Cell', parent=styles['Normal'], fontName='Times-Roman', fontSize=12)

    elements = []
    elements.append(Paragraph("Liste des prises en charge", title_style))
    elements.append(Spacer(1, 20))

    for prise in prises:
        data = [
            ['Objet', prise.objet],
            ['Description', prise.description or ''],
            ['Date création', prise.date_creation.strftime('%d/%m/%Y %H:%M')],
            ['Nom médecin', prise.nom_complet_medecin or ''],
            ['Fonction médecin', prise.fonction_medecin or ''],
            ['Spécialité médecin', prise.specialite_medecin or ''],
            ['Adhérent', f"{prise.adherent.last_name} {prise.adherent.first_name}"],
        ]
        table = Table(data, colWidths=[150, 300])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))  # espace entre les prises en charge

    return elements  # retourne une liste de Flowables pour intégration dans PDF


# === Détail d'une prise en charge ===
def prise_en_charge_print_detail(request, pk):
    prise = get_object_or_404(PriseEnChargeAdherent, pk=pk)

    # Pour PDF : création d'une liste de Flowables
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Title', parent=styles['Title'], fontName='Times-Bold', fontSize=16)
    cell_style = ParagraphStyle(name='Cell', parent=styles['Normal'], fontName='Times-Roman', fontSize=12)

    elements = []
    elements.append(Paragraph(f"Prise en charge : {prise.objet}", title_style))
    elements.append(Spacer(1, 20))

    data = [
        [Paragraph("Champ", title_style), Paragraph("Valeur", title_style)],
        [Paragraph("Objet", cell_style), Paragraph(prise.objet, cell_style)],
        [Paragraph("Description", cell_style), Paragraph(prise.description or '', cell_style)],
        [Paragraph("Date de création", cell_style), Paragraph(prise.date_creation.strftime('%d/%m/%Y %H:%M'), cell_style)],
        [Paragraph("Nom médecin", cell_style), Paragraph(prise.nom_complet_medecin or '', cell_style)],
        [Paragraph("Fonction médecin", cell_style), Paragraph(prise.fonction_medecin or '', cell_style)],
        [Paragraph("Spécialité médecin", cell_style), Paragraph(prise.specialite_medecin or '', cell_style)],
        [Paragraph("Adhérent", cell_style), Paragraph(f"{prise.adherent.last_name} {prise.adherent.first_name}", cell_style)],
        [Paragraph("Opération enregistrée", cell_style), Paragraph(str(prise.operation_enregistrer), cell_style)],
        [Paragraph("Opération médecin", cell_style), Paragraph(str(prise.operation_medecin) if prise.operation_medecin else '', cell_style)],
    ]

    from reportlab.platypus import Table
    table = Table(data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table)

    # Si besoin, tu peux rendre un template HTML pour affichage web
    if request.GET.get('format') == 'html':
        return render(request, 'Prise_en_charge_adherent/prise_en_charge_print_detail.html', {
            'prise': prise
        })

    return elements  # retourne une liste de Flowables pour utilisation dans un PDF

from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from .models import PriseEnChargeAdherent

def adherent_prises_en_charge_print_pdf(adherent):
    """
    Retourne une liste de Flowables représentant les prises en charge
    pour un adhérent donné. Ne crée pas de page si aucune prise en charge.
    """
    prises = PriseEnChargeAdherent.objects.filter(adherent=adherent).order_by('-date_creation')
    elements = []

    if prises.exists():
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(name='Title', parent=styles['Title'], fontName='Times-Bold', fontSize=14)

        elements.append(Paragraph("Prises en charge de l'adhérent", title_style))
        elements.append(Spacer(1, 20))

        for prise in prises:
            data = [
                ['Objet', prise.objet or ''],
                ['Description', prise.description or ''],
                ['Date création', prise.date_creation.strftime('%d/%m/%Y %H:%M') if prise.date_creation else ''],
                ['Nom médecin', prise.nom_complet_medecin or ''],
                ['Fonction médecin', prise.fonction_medecin or ''],
                ['Spécialité médecin', prise.specialite_medecin or ''],
            ]
            table = Table(data, colWidths=[150, 300])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 20))

    # Toujours retourner une liste, même vide, pour compatibilité avec la fusion PDF
    return elements
