from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from reportlab.pdfgen import canvas
from Gestion_personnel.operation.vew_print1 import generer_pied_structure_pdf
from referentiel.structure.models import Structure
from referentiel.structure.vew_impression import generer_entete_structure_pdf
from .models import SuiviTuteurAdherent
from .forms import SuiviTuteurAdherentForm
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


# Liste des suivis Tuteur-Adhérent
def suivi_list(request):
    query = request.GET.get('q', '').strip()
    suivis_qs = SuiviTuteurAdherent.objects.all().order_by('-date_creation')

    if query:
        suivis_qs = suivis_qs.filter(
            Q(adherent__first_name__icontains=query) |
            Q(adherent__last_name__icontains=query) |
            Q(tuteur__first_name__icontains=query) |
            Q(tuteur__last_name__icontains=query)
        )

    paginator = Paginator(suivis_qs, 10)
    page_number = request.GET.get('page')
    suivis = paginator.get_page(page_number)

    return render(request, 'suiviTuteurAdherent/suivi_list.html', {
        'suivis': suivis,
        'query': query,
    })


# Création d'un suivi
def suivi_create(request):
    if request.method == 'POST':
        form = SuiviTuteurAdherentForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Suivi Tuteur-Adhérent enregistré avec succès.")
                if request.POST.get("action") == "save_and_new":
                    return redirect('suivi_tuteur:suivi_create')
                return redirect('suivi_tuteur:suivi_list')
            except ValueError as e:
                form.add_error(None, str(e))
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        form = SuiviTuteurAdherentForm()

    return render(request, 'suiviTuteurAdherent/suivi_form.html', {
        'form': form,
        'mode': 'ajouter',
    })


# Modification d'un suivi
def suivi_update(request, pk):
    suivi = get_object_or_404(SuiviTuteurAdherent, pk=pk)

    if request.method == 'POST':
        form = SuiviTuteurAdherentForm(request.POST, instance=suivi)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Suivi Tuteur-Adhérent mis à jour.")
                return redirect('suivi_tuteur:suivi_list')
            except ValueError as e:
                form.add_error(None, str(e))
        else:
            messages.error(request, "Merci de corriger les erreurs dans le formulaire.")
    else:
        form = SuiviTuteurAdherentForm(instance=suivi)

    return render(request, 'suiviTuteurAdherent/suivi_form.html', {
        'form': form,
        'mode': 'modifier',
        'suivi': suivi,
    })


# Recherche de suivi
def suivi_search(request):
    query = request.GET.get('q', '').strip()
    if query:
        suivis = SuiviTuteurAdherent.objects.filter(
            Q(adherent__first_name__icontains=query) |
            Q(adherent__last_name__icontains=query) |
            Q(tuteur__first_name__icontains=query) |
            Q(tuteur__last_name__icontains=query)
        ).order_by('-date_creation')
    else:
        suivis = SuiviTuteurAdherent.objects.all().order_by('-date_creation')
    paginator = Paginator(suivis, 10)
    page_number = request.GET.get('page')
    suivis = paginator.get_page(page_number)
    return render(request, 'suiviTuteurAdherent/suivi_search.html', {
        'suivis': suivis,
        'query': query,
    })


# Archivage / désarchivage d'un suivi
def suivi_archive(request, pk):
    suivi = get_object_or_404(SuiviTuteurAdherent, pk=pk)
    # Ici tu peux décider si tu veux supprimer ou changer un statut "actif/inactif"
    suivi.delete()
    messages.success(request, "Suivi Tuteur-Adhérent supprimé avec succès.")
    return redirect('suivi_tuteur:suivi_list')


# Archivage / réactivation en groupe
def suivi_archive_group(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids')
        suivis = SuiviTuteurAdherent.objects.filter(id__in=ids)
        count = suivis.count()
        suivis.delete()
        messages.success(request, f"{count} suivi(s) supprimé(s) avec succès.")
    return redirect('suivi_tuteur:suivi_list')


# Impression / export PDF (exemple simple)
def suivi_print_detail(request, pk):
    # Récupérer le suivi
    # Essayer de récupérer un suivi précis
    suivi = SuiviTuteurAdherent.objects.filter(pk=pk).first()

    if suivi:
        suivis = [suivi]  # liste pour uniformité
    else:
        # Si aucun suivi avec ce PK, considérer pk comme id_adherent
        suivis = SuiviTuteurAdherent.objects.filter(adherent_id=pk)
        if not suivis.exists():
            return HttpResponse("Aucun suivi trouvé pour cet adhérent ou ce suivi.", status=404)

    # Préparer la réponse PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="suivi_tuteur_adherent_{suivi.id}.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        topMargin=50,
        leftMargin=50,
        rightMargin=50,
        bottomMargin=50,
    )

    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name='TitleTimes',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=16,
        leading=20,
    )

    cell_style = ParagraphStyle(
        name='CellStyleTimes',
        fontName='Times-Roman',
        fontSize=12,
        leading=14,
    )

    elements.append(Paragraph(f"Suivi Tuteur-Adhérent : {suivi.adherent.last_name} {suivi.adherent.first_name}", title_style))
    elements.append(Spacer(1, 20))

    # Préparer les données pour le tableau
    data = [
        [Paragraph("Champ", title_style), Paragraph("Valeur", title_style)],
        [Paragraph("Adhérent", cell_style), Paragraph(f"{suivi.adherent.last_name} {suivi.adherent.first_name}", cell_style)],
        [Paragraph("Tuteur", cell_style), Paragraph(f"{suivi.tuteur.last_name} {suivi.tuteur.first_name}", cell_style)],
        [Paragraph("Statut", cell_style), Paragraph(suivi.get_statut_display(), cell_style)],
        [Paragraph("Date création", cell_style), Paragraph(suivi.date_creation.strftime('%d/%m/%Y %H:%M'), cell_style)],
    ]

    table = Table(data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # Générer le PDF
    doc.build(elements)
    return response



def suivi_print_list(request):
    suivis = SuiviTuteurAdherent.objects.select_related('adherent', 'tuteur').order_by('-date_creation')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="suivi_tuteur_adherent.pdf"'
    structure = Structure.objects.first()
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        topMargin=50,
        leftMargin=50,
        rightMargin=50,
        bottomMargin=50,
    )

    elements = []
    styles = getSampleStyleSheet()

    # Titre
    title_style = ParagraphStyle(
        name='TitleTimes',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=18,
        leading=22,
    )
    elements.append(Spacer(1, 250))
    elements.append(Paragraph("Liste des Suivis Tuteur-Adhérent", title_style))
    elements.append(Spacer(1, 20))

    # Style pour le contenu des cellules
    cell_style = ParagraphStyle(
        name='CellStyleTimes',
        fontName='Times-Roman',
        fontSize=12,
        leading=14,
    )

    # Données du tableau
    data = [
        [
            Paragraph("Adhérent", title_style),
            Paragraph("Tuteur", title_style),
            Paragraph("Statut", title_style),
            Paragraph("Date création", title_style)
        ]
    ]

    for suivi in suivis:
        data.append([
            Paragraph(f"{suivi.adherent.last_name} {suivi.adherent.first_name}", cell_style),
            Paragraph(f"{suivi.tuteur.last_name} {suivi.tuteur.first_name}", cell_style),
            Paragraph(suivi.get_statut_display(), cell_style),
            Paragraph(suivi.date_creation.strftime('%d/%m/%Y %H:%M'), cell_style),
        ])

    table = Table(data, colWidths=[150, 150, 60, 120], splitByRow=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
         ("FONTSIZE", (0, 0), (-1, 0), 10),
    ]))
    elements.append(table)

    # Canvas personnalisé

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
    doc.build(elements,  canvasmaker=CustomCanvas)

    return response
