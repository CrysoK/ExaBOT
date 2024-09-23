# DEPENDENCIAS ################################################################

# fmt: off
import logging
from math import e
logging.basicConfig(level=logging.INFO)

import sys  # noqa E402
sys.path.append("config.py")

import discord as ds  # noqa E402
from discord.ext import commands, tasks  # noqa E402

from dotenv import load_dotenv  # noqa E402
load_dotenv(override=True)

import config as cfg  # noqa E402

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

# bot = commands.Bot(
#     command_prefix=["."],
#     # Intents de Discord para el bot.
#     intents=ds.Intents.all(),
#     # help_command=Ayuda(
#     #     commands_heading="Comandos",
#     #     aliases_heading="Alias",
#     #     no_category="Sin categoría",
#     #     command_attrs={
#     #         "name": "ayuda",
#     #         "aliases": ["help", "h", "comandos", "cmds", "cmd"],
#     #     },
#     # ),
# )

bot = ds.Bot(
    command_prefix=["."],
    intents=ds.Intents.all(),
    debug_guilds=[839277844257570846],
)

# Cargar extensiones por defecto
for ext in cfg.EXT_DEFAULT:
    bot.load_extension(f"{cfg.EXT}.{ext}")


# MONITOREO ###################################################################


@tasks.loop(minutes=5, reconnect=False)
async def heartbeat():
    if bot.is_closed():
        # La conexión a Discord está cerrada.
        heartbeat.stop()
    with requests.post(cfg.HEARTBEAT_URL) as r:
        if r.status_code == 200:
            print("Heartbeat enviado.")
        else:
            print(f"Error al enviar heartbeat: {r.status_code}")


@heartbeat.before_loop
async def before_heartbeat():
    await bot.wait_until_ready()


@heartbeat.after_loop
async def after_heartbeat():
    if bot.is_closed() or heartbeat.is_being_cancelled():
        # La conexión a Discord está cerrada o el loop ha sido cancelado (por
        # ejemplo al finalizar el bot).
        url = cfg.HEARTBEAT_URL + "/fail"
        with requests.post(url, data="Heartbeat loop finalizado") as r:
            if r.status_code == 200:
                print("Terminación notificada.")
            else:
                print(f"Error al notificar terminación: {r.status_code}")
    else:
        # La conexión se restableció (?)
        heartbeat.start()


# EVENTOS #####################################################################


@bot.event
async def on_ready():
    print(f"Sesión iniciada como {bot.user} (ID: {bot.user.id})")
    heartbeat.start()
    await actualizar_presencia(bot)


@bot.event
async def on_guild_join(guild: ds.Guild):
    espacio = Espacios.objects(_id=guild.id).first()
    if not espacio:
        espacio = Espacios(_id=guild.id)
        espacio.save()
        print(f'Espacio "{guild.name}" añadido a la base de datos')
    else:
        print(f'El espacio "{guild.name}" ya estaba en la base de datos')


"""
¿Debería eliminar todos los datos de la base de datos o eso debería ser un
comando (por ejemplo, `restablecer_bot`)?
Respuesta: comando
"""


@bot.event
async def on_command_error(ctx, error):
    # TODO: Traducir todos los errores.
    # await ctx.send(error)
    print(error)  # debug
    try:
        await ctx.respond(ERRORES[error.__class__.__name__].format(**attr2dict(error)))
    except Exception as e:
        print(e)  # debug


@bot.event
async def on_application_error(ctx, error):
    print(error)  # debug
    try:
        await ctx.respond(ERRORES[error.__class__.__name__].format(**attr2dict(error)))
    except Exception as e:
        print(e)  # debug


# EJECUCIÓN ###################################################################

bot.run(cfg.BOT_TOKEN)

print("<?> Ejecutado: main.py")

# EOF #########################################################################
