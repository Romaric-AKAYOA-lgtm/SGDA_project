from reportlab.platypus import  Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from Gestion_personnel.absence.models import Absence
from Gestion_personnel.operation.models import Operation

def generer_pdf_absences_employe(employe):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Title', parent=styles['Title'], fontName='Times-Bold', fontSize=16)
    header_style = ParagraphStyle(name='Header', fontName='Times-Bold', fontSize=10, alignment=1)
    cell_style = ParagraphStyle(name='Cell', fontName='Times-Roman', fontSize=10)

    operations = Operation.objects.filter(id_employe=employe)
    absences = Absence.objects.filter(id_absence_operation_employe__in=operations).order_by('-date_debut')

    elements = []
    titre = f"Liste des absences de l'employé : {employe.last_name} {employe.first_name}"
    elements.append(Paragraph(titre, title_style))
    elements.append(Spacer(1, 12))

    if absences.exists():
        data = [[
            Paragraph("Type", header_style),
            Paragraph("Date début", header_style),
            Paragraph("Durée", header_style),
            Paragraph("Date retour", header_style),
            Paragraph("Date retour effective", header_style),
            Paragraph("Statut", header_style),
            Paragraph("Lieu", header_style),
            Paragraph("Motif", header_style),
            Paragraph("N° Note", header_style),
            Paragraph("N° Fiche", header_style),
        ]]

        for absence in absences:
            data.append([
                Paragraph(absence.get_type_absence_display(), cell_style),
                Paragraph(absence.date_debut.strftime("%d/%m/%Y %H:%M"), cell_style),
                Paragraph(str(absence.duree), cell_style),
                Paragraph(absence.date_retour.strftime("%d/%m/%Y"), cell_style),
                Paragraph(absence.date_retour_effective.strftime("%d/%m/%Y") if absence.date_retour_effective else "Non retourné", cell_style),
                Paragraph(absence.get_statut_display(), cell_style),
                Paragraph(absence.lieu or "", cell_style),
                Paragraph(absence.motif or "", cell_style),
                Paragraph(str(absence.numero_note or ""), cell_style),
                Paragraph(str(absence.numero_fiche or ""), cell_style),
            ])

        table = Table(data, repeatRows=1, colWidths=[60] * 10)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("Aucune absence enregistrée pour cet employé.", cell_style))

    # Ajout d'un margin bottom global (espace en bas)
    elements.append(Spacer(20, 30))  # 20 points d'espace en bas

    return elements  # ✅ liste de Flowables

