from django.db.models import Q
from django.utils.timezone import localtime, now as timezone_now
from Gestion_personnel.operation.models import Operation

from reportlab.platypus import  Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generer_pied_structure_pdf(p):
    width, height = A4
    x_offset_right = width - 200
    margin_top = 50
    y_infos = 200 - margin_top

    date_du_jour = localtime().strftime("%d/%m/%Y")
    maintenant = timezone_now()

    try:
        # ✅ Récupère la dernière opération de mutation confirmée
        operation = Operation.objects.select_related('id_employe', 'id_fonction').filter(
            type_operation='mutation',
            statut='confirme',
            id_fonction__fonction_parent__isnull=True,
        ).filter(
            Q(date_fin__isnull=True) | Q(date_fin__gte=maintenant)
        ).order_by('-date_debut').first()

        if operation:
            employe = operation.id_employe
            nom = employe.last_name.upper() if employe.last_name else "NOM"
            prenom = employe.first_name if employe.first_name else "Prénom"
            fonction = operation.id_fonction.designation if operation.id_fonction else "Fonction inconnue"

            # ✅ Déterminer l'article selon le sexe
            if employe.sexe == "F":
                article = "La"
            else:
                article = "Le"
        else:
            nom = "NOM INCONNU"
            prenom = "Prénom inconnu"
            fonction = "Fonction inconnue"
            article = "Le"
    except Exception:
        nom = "NOM INCONNU"
        prenom = "Prénom inconnu"
        fonction = "Fonction inconnue"
        article = "Le"

    # ✅ Génération du pied du PDF
    p.setFont("Times-Roman", 10)
    p.drawString(x_offset_right, y_infos, f"Fait à Brazzaville, le {date_du_jour}")
    p.drawString(x_offset_right, y_infos - 100, f"{nom} {prenom}")
    p.drawString(x_offset_right, y_infos - 115, f"{article} {fonction}")



def generer_pdf_operations_employe(employe):
    operations = Operation.objects.filter(id_employe=employe).order_by('-date_debut')
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Title', parent=styles['Title'], fontName='Times-Bold', fontSize=16)
    header_style = ParagraphStyle(name='Header', fontName='Times-Bold', fontSize=10, alignment=1)
    cell_style = ParagraphStyle(name='Cell', fontName='Times-Roman', fontSize=10)

    elements = []

    elements.append(Paragraph(f"Liste des opérations de l'employé : {employe.last_name} {employe.first_name}", title_style))
    elements.append(Spacer(1, 12))

    if operations.exists():
        data = [[
            Paragraph("Date début", header_style),
            Paragraph("Date fin", header_style),
            Paragraph("Statut", header_style),
            Paragraph("N° Note", header_style),
            Paragraph("N° Fiche", header_style),
            Paragraph("Type", header_style),
            Paragraph("Unité", header_style),
            Paragraph("Fonction", header_style),
            Paragraph("Responsable", header_style),
            Paragraph("Enregistreur", header_style),
        ]]

        for op in operations:
            data.append([
                Paragraph(op.date_debut.strftime("%d/%m/%Y %H:%M") if op.date_debut else "", cell_style),
                Paragraph(op.date_fin.strftime("%d/%m/%Y %H:%M") if op.date_fin else "En cours", cell_style),
                Paragraph(op.get_statut_display(), cell_style),
                Paragraph(str(op.numero_note or ""), cell_style),
                Paragraph(str(op.numero_fiche or ""), cell_style),
                Paragraph(op.get_type_operation_display(), cell_style),
                Paragraph(str(op.id_organisation_unite or ""), cell_style),
                Paragraph(str(op.id_fonction or ""), cell_style),
                Paragraph(str(op.id_employe_respensable or ""), cell_style),
                Paragraph(str(op.id_employe_enregitre or ""), cell_style),
            ])

        table = Table(data, repeatRows=1, colWidths=[70] * 10)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        elements.append(table)
    else:
        elements.append(Paragraph("Aucune opération trouvée pour cet employé.", cell_style))

    # Ajout d'un margin bottom global (espace en bas)
    elements.append(Spacer(20, 30))  # 20 points d'espace en bas
    return elements  # ✅ Retourne une liste de Flowables, pas un buffer

