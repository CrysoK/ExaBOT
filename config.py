# NO MODIFICABLE ##############################################################

import os
import logging

logger = logging.getLogger(__name__)

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

# No incluir timestamp en logs
NO_TIMESTAMPS = os.getenv("NO_TIMESTAMPS")
LOG_FORMAT = (
    f"[{'' if NO_TIMESTAMPS else '%(asctime)s '}%(levelname)s %(name)s] %(message)s"
)
LOG_LEVEL = os.getenv("LOG_LEVEL", logging.INFO)

logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)

DEBUG_GUILDS = None
try:
    DEBUG_GUILDS = [int(x.strip()) for x in os.environ["DEBUG_GUILDS"].split(",")]
    logger.info("DEBUG_GUILDS activo. No se registrarán comandos globalmente.")
except ValueError:
    logger.error("Valor inválido en la variable de entorno DEBUG_GUILDS.")
except KeyError:
    logger.info("No se indicaron espacios para depuración.")

# Carpeta de extensiones
EXT = "ext"
EXT_DEFAULT = [
    "bot",
    "registros",
    "otros",
    "auto_reaccion",
    # "ia"  # No disponible por el momento
]

logger.info("Ejecutado: config.py")
