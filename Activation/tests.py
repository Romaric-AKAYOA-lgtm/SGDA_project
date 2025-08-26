from datetime import datetime
import uuid

# Générer l'UUID
activation_key = str(uuid.uuid4())

# Ajouter la date actuelle sous le format YYYYMMDDHHMM
activation_date = datetime.now().strftime("202509030012M")

# Concaténer l'UUID et la date pour créer la clé d'activation
activation_key_full = f"{activation_key}-{activation_date}"

# Afficher la clé générée
print(activation_key_full)
