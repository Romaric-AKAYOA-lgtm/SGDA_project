import os
import subprocess
from dotenv import load_dotenv
from datetime import datetime, timedelta
import mysql.connector

# =========================
# Charger le fichier .env
# =========================
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)

# =========================
# Variables de connexion
# =========================
DB_USER = os.getenv('DB_USER', '').strip()
DB_PASS = os.getenv('DB_PASSWORD', '').strip()
DB_NAME = os.getenv('DB_NAME', '').strip()
DB_HOST = os.getenv('DB_HOST', '127.0.0.1').strip()
DB_PORT = int(os.getenv('DB_PORT', 3306))

# =========================
# Vérification des variables d'environnement
# =========================
missing_vars = []
for var_name in ["DB_USER", "DB_PASSWORD", "DB_NAME", "DB_HOST"]:
    if not os.getenv(var_name):
        missing_vars.append(var_name)

if missing_vars:
    raise ValueError(f"Les variables d'environnement suivantes doivent être définies dans .env : {', '.join(missing_vars)}")

# Affichage pour debug (facultatif)
"""   
print("Variables d'environnement chargées :")
print("DB_USER:", DB_USER)
print("DB_NAME:", DB_NAME)
print("DB_HOST:", DB_HOST)
print("DB_PORT:", DB_PORT)
"""
# =========================
# Répertoire de sauvegarde
# =========================
BACKUP_DIR = os.path.join(os.path.dirname(__file__), "transaction")
os.makedirs(BACKUP_DIR, exist_ok=True)

# =========================
# Chemin vers mysqldump
# =========================
MYSQLDUMP = r"C:\xampp\mysql\bin\mysqldump.exe"
if not os.path.exists(MYSQLDUMP):
    raise FileNotFoundError(f"mysqldump introuvable : {MYSQLDUMP}")

# =========================
# Fichier pour mémoriser la dernière sauvegarde complète
# =========================
LAST_FULL_FILE = os.path.join(BACKUP_DIR, "last_full.txt")

# =========================
# Connexion MySQL
# =========================
def get_tables():
    """Retourne la liste des tables de la base."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME, port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [t[0] for t in cursor.fetchall()]
        cursor.close()
        conn.close()
        return tables
    except Exception as e:
        raise ConnectionError(f"Impossible de récupérer les tables : {e}")

# =========================
# Déterminer la date de dernière sauvegarde complète
# =========================
def get_last_full_date():
    today = datetime.now().date()
    if os.path.exists(LAST_FULL_FILE):
        with open(LAST_FULL_FILE) as f:
            try:
                return datetime.strptime(f.read().strip(), "%Y-%m-%d").date()
            except:
                return today - timedelta(days=6)
    return today - timedelta(days=6)

# =========================
# Fonctions sauvegarde
# =========================
def backup_full():
    """Effectue une sauvegarde complète de la base."""
    today = datetime.now().date()
    date_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file = os.path.join(BACKUP_DIR, f"save_complet_{DB_NAME}_{date_time}.sql")
    cmd = f'"{MYSQLDUMP}" -h {DB_HOST} -u {DB_USER} -p"{DB_PASS}" --single-transaction --routines --triggers "{DB_NAME}"'
    subprocess.run(cmd, shell=True, stdout=open(file, 'w', encoding='utf-8'), stderr=subprocess.PIPE)
    with open(LAST_FULL_FILE, 'w') as f:
        f.write(today.strftime("%Y-%m-%d"))


def backup_diff():
    """Effectue une sauvegarde différentielle basée sur les dates min des colonnes spécifiques."""
    today = datetime.now().date()
    tables = get_tables()
    date_columns = ["date_creation","date_enregistrement","date_visite","date_annulation"]
    date_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file = os.path.join(BACKUP_DIR, f"save_differentiel_{DB_NAME}_{date_time}.sql")
    
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME, port=DB_PORT
        )
        cursor = conn.cursor()
        with open(file, 'w', encoding='utf-8') as f:
            for table in tables:
                for col in date_columns:
                    try:
                        cursor.execute(f"SHOW COLUMNS FROM `{table}` LIKE '{col}'")
                        if cursor.fetchone():
                            cursor.execute(f"SELECT MIN({col}) FROM `{table}`")
                            min_date = cursor.fetchone()[0] or today
                            min_date_str = min_date.strftime("%Y-%m-%d")
                            cmd = f'"{MYSQLDUMP}" -h {DB_HOST} -u {DB_USER} -p"{DB_PASS}" --single-transaction "{DB_NAME}" `{table}` --where="{col} >= \'{min_date_str}\'"'
                            subprocess.run(cmd, shell=True, stdout=f, stderr=subprocess.PIPE)
                            break
                    except:
                        continue
        cursor.close()
        conn.close()
    except Exception as e:
        raise ConnectionError(f"Erreur lors de la sauvegarde différentielle : {e}")
