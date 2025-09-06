@echo off
REM Aller dans le dossier où se trouve ce fichier .bat
cd /d "%~dp0"

REM Lancer le script Python qui démarre Django et ouvre le navigateur
start "" python demarrer_projet.py
>python run_backup.py

REM Fermer automatiquement le terminal après exécution
exit
