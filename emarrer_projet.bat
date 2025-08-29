@echo off
REM Aller dans le dossier où se trouve ce fichier .bat
cd /d "%~dp0"

REM Lancer le script Python qui démarre Django et ouvre le navigateur
python demarrer_projet.py

REM Fermer automatiquement le terminal après exécution
exit
