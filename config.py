# NO MODIFICABLE ##############################################################

import os

# MODIFICABLE #################################################################

# Las variables globales pueden indicarse en un archivo .env
# El resto puede modificarse directamente en este archivo.

# BOT
BOT_TOKEN = os.environ["BOT_TOKEN"]

# MongoDB
MONGODB_URI = os.environ["MONGODB_URI"]
DB_NAME = os.environ["DB_NAME"]

# Carpeta de extensiones
EXT = "ext"
EXT_DEFAULT = ["Bot", "Saludos", "Others", "AutoReaccion"]

print("<?> Ejecutado: config.py")
