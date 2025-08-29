#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from dotenv import load_dotenv
from django.conf import settings

# Charger le fichier .env
load_dotenv()

# Récupérer IP et PORT depuis le fichier .env
IP = os.getenv("DJANGO_IP", "127.0.0.1")
PORT = os.getenv("DJANGO_PORT", "8000")

# Définir les commandes à bloquer en production
#DISABLE_MANAGE_COMMANDS = ['createsuperuser', 'flush','makemigrations','migrate', 'dbshell']
DISABLE_MANAGE_COMMANDS = []

def main():
    """Run administrative tasks."""
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE',
        'SGDA_project.settings'
    )

    # Vérifier si la commande est interdite
    cmd = sys.argv[1] if len(sys.argv) > 1 else None
    if cmd in DISABLE_MANAGE_COMMANDS:
        print(f"La commande '{cmd}' est désactivée en production !")
        sys.exit(1)

    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SGDA_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # Lancer le serveur sur IP:PORT si c'est runserver
    if len(sys.argv) == 1 or sys.argv[1] != 'runserver':
        execute_from_command_line(sys.argv)
    else:
        execute_from_command_line([sys.argv[0], 'runserver', f"{IP}:{PORT}"])

if __name__ == '__main__':
    main()
