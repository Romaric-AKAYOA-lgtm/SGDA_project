import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from threading import Thread

# compte/backup_middleware.py
from .run_backup import backup_diff, backup_full  # fonctions déjà sans arguments

load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

BACKUP_DIR = os.getenv("BACKUP_DIR", "transaction")
FULL_INTERVAL = int(os.getenv("FULL_BACKUP_INTERVAL_DAYS", 5))
DIFF_HOUR = int(os.getenv("DIFF_BACKUP_HOUR", 13))


def perform_backup():
    today = datetime.now().date()
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # Sauvegarde complète
    last_full_file = os.path.join(BACKUP_DIR, "last_full.txt")
    if os.path.exists(last_full_file):
        with open(last_full_file) as f:
            try:
                last_full = datetime.strptime(f.read().strip(), "%Y-%m-%d").date()
            except Exception:
                last_full = today - timedelta(days=FULL_INTERVAL + 1)
    else:
        last_full = today - timedelta(days=FULL_INTERVAL + 1)

    if (today - last_full).days >= FULL_INTERVAL:
        backup_full()  # plus d’arguments
        with open(last_full_file, 'w') as f:
            f.write(today.strftime("%Y-%m-%d"))

    # Sauvegarde différentielle
    last_diff_file = os.path.join(BACKUP_DIR, "last_diff.txt")
    if os.path.exists(last_diff_file):
        with open(last_diff_file) as f:
            try:
                last_diff = datetime.strptime(f.read().strip(), "%Y-%m-%d").date()
            except Exception:
                last_diff = today - timedelta(days=1)
    else:
        last_diff = today - timedelta(days=1)

    current_hour = datetime.now().hour
    if current_hour == DIFF_HOUR and last_diff < today:
        backup_diff()  # plus d’arguments
        with open(last_diff_file, 'w') as f:
            f.write(today.strftime("%Y-%m-%d"))


class BackupMiddleware:
    """Middleware pour lancer les sauvegardes de manière asynchrone"""
    def __init__(self, get_response):
        self.get_response = get_response
        # Lancer la sauvegarde dès l'initialisation du middleware dans un thread
        Thread(target=perform_backup, daemon=True).start()

    def __call__(self, request):
        response = self.get_response(request)
        return response
