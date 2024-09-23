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

# ChatGPT
OPENAI_ACCESS_TOKEN = os.getenv("OPENAI_ACCESS_TOKEN")

# Monitoreo (BetterStack)
HEARTBEAT_URL = os.environ["HEARTBEAT_URL"]

# Carpeta de extensiones
EXT = "ext"
EXT_DEFAULT = [
    "bot",
    "registros",
    "otros",
    "auto_reaccion",
    # "ia"  # No disponible por el momento
]

print("<?> Ejecutado: config.py")
