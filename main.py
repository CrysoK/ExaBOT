# DEPENDENCIAS ################################################################

# fmt: off
from dotenv import load_dotenv  # noqa E402
load_dotenv(override=True)

import config as cfg  # noqa E402

import logging
logger = logging.getLogger("main")

import discord as ds  # noqa E402
from discord.ext import commands, tasks  # noqa E402

import mongoengine as mongo  # noqa E402

from colecciones import Espacios

import requests

from utils import (  # noqa E402
    ERRORES,
    array_natural,
    actualizar_presencia,
    attr2dict
)
# fmt: on

# INICIALIZACIÓN ##############################################################


# Comando de ayuda personalizado que hereda del comando por defecto.
class Ayuda(commands.DefaultHelpCommand):
    pass


# Conexión a la base de datos.
mongo.connect(db=cfg.DB_NAME, host=cfg.MONGODB_URI)

bot = ds.Bot(
    command_prefix=["."],
    intents=ds.Intents.all(),
    debug_guilds=cfg.DEBUG_GUILDS,
)

# Cargar extensiones por defecto
for ext in cfg.EXT_DEFAULT:
    bot.load_extension(f"{cfg.EXT}.{ext}")


# MONITOREO ###################################################################


@tasks.loop(minutes=5)
async def heartbeat():
    if bot.is_closed():
        logger.error("La conexión a Discord está cerrada")
        return
    r = requests.post(cfg.HEARTBEAT_URL)
    if r.status_code == 200:
        logger.debug("Heartbeat enviado.")
    else:
        logger.error(f"Error al enviar heartbeat: {r.status_code}")
    r.close()


# EVENTOS #####################################################################


@bot.event
async def on_ready():
    logger.info(f"Sesión iniciada como {bot.user} (ID: {bot.user.id})")
    if cfg.HEARTBEAT_URL:
        try:
            heartbeat.start()  # Iniciar monitoreo al iniciar sesión
        except Exception as e:
            logger.error(e)
    await actualizar_presencia(bot)


@bot.event
async def on_resume():
    await actualizar_presencia(bot)


@bot.event
async def on_guild_join(guild: ds.Guild):
    espacio = Espacios.objects(_id=guild.id).first()
    if not espacio:
        espacio = Espacios(_id=guild.id)
        espacio.save()
        logger.info(f'Espacio "{guild.name}" añadido a la base de datos')
    else:
        logger.info(f'El espacio "{guild.name}" ya estaba en la base de datos')


"""
¿Debería eliminar todos los datos de la base de datos o eso debería ser un
comando (por ejemplo, `restablecer_bot`)?
Respuesta: comando
"""


@bot.event
async def on_command_error(ctx, error):
    # TODO: Traducir todos los errores.
    # await ctx.send(error)
    logger.debug(error)  # debug
    try:
        await ctx.respond(ERRORES[error.__class__.__name__].format(**attr2dict(error)))
    except Exception as e:
        logger.debug(e)  # debug


@bot.event
async def on_application_error(ctx, error):
    logger.debug(error)  # debug
    try:
        await ctx.respond(ERRORES[error.__class__.__name__].format(**attr2dict(error)))
    except Exception as e:
        logger.debug(e)  # debug


# EJECUCIÓN ###################################################################

bot.run(cfg.BOT_TOKEN)

logger.info("Ejecutado: main.py")

# EOF #########################################################################
