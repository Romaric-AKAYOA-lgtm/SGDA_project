import threading
import webbrowser
import time
import sys
import os
from dotenv import load_dotenv

# Charger dotenv avant tout
load_dotenv()

# Définir la variable d'environnement pour Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SGDA_project.settings')

# Récupérer IP et PORT depuis le .env
IP = os.getenv("DJANGO_IP", "127.0.0.1")
PORT = os.getenv("DJANGO_PORT", "8000")
URL = f"http://{IP}:{PORT}"

# Importer Django après avoir défini DJANGO_SETTINGS_MODULE
from django.core.management import execute_from_command_line

# Fonction pour ouvrir le navigateur
def open_browser():
    time.sleep(3)  # attendre que le serveur démarre
    webbrowser.open(URL)

# Lancer le navigateur dans un thread séparé
threading.Thread(target=open_browser).start()

# Lancer Django dans le thread principal (obligatoire pour signal)
sys.argv = ["manage.py", "runserver", f"{IP}:{PORT}"]
execute_from_command_line(sys.argv)
