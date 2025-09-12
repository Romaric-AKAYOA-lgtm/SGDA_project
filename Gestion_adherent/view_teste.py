import os
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PyPDF2 import PdfReader
import docx
import openpyxl
from django.utils.text import get_valid_filename

@csrf_exempt
def upload_files(request):
    if request.method == "POST":
        fichier = request.FILES.get("file")
        dossier = request.POST.get("dossier")  # l'utilisateur fournit le chemin du dossier

        if not fichier:
            return JsonResponse({"error": "Aucun fichier reçu"}, status=400)
        if not dossier:
            return JsonResponse({"error": "Aucun dossier sélectionné"}, status=400)

        # Nettoyer le nom du fichier pour éviter les problèmes
        safe_filename = get_valid_filename(fichier.name)
        dossier = os.path.abspath(dossier)  # chemin absolu pour plus de sécurité

        # Créer le dossier si nécessaire
        os.makedirs(dossier, exist_ok=True)

        # Chemin complet du fichier
        file_path = os.path.join(dossier, safe_filename)

        # Sauvegarder le fichier
        with open(file_path, "wb+") as destination:
            for chunk in fichier.chunks():
                destination.write(chunk)

        # Détecter le type de fichier et extraire le contenu
        extracted_data = ""
        if safe_filename.lower().endswith(".pdf"):
            extracted_data = extract_pdf(file_path)
        elif safe_filename.lower().endswith(".docx"):
            extracted_data = extract_word(file_path)
        elif safe_filename.lower().endswith(".xlsx"):
            extracted_data = extract_excel(file_path)
        else:
            extracted_data = "Type de fichier non pris en charge"

        return JsonResponse({
            "message": f"Fichier uploadé avec succès dans {dossier}",
            "extracted": extracted_data
        })

    return render(request, "Gestion_adherent/upload.html")


def extract_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        return f"Erreur lors de l'extraction PDF: {e}"


def extract_word(file_path):
    try:
        doc = docx.Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        return f"Erreur lors de l'extraction Word: {e}"


def extract_excel(file_path):
    try:
        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheet = wb.active
        data = ""
        for row in sheet.iter_rows(values_only=True):
            data += " | ".join([str(cell) if cell is not None else "" for cell in row]) + "\n"
        return data.strip()
    except Exception as e:
        return f"Erreur lors de l'extraction Excel: {e}"
