# DEPENDENCIAS ################################################################

# fmt: off
import logging
from math import e
logging.basicConfig(level=logging.INFO)

import sys  # noqa E402
sys.path.append("config.py")

import discord as ds  # noqa E402
from discord.ext import commands  # noqa E402

from dotenv import load_dotenv  # noqa E402
load_dotenv(override=True)

import config as cfg  # noqa E402

import mongoengine as mongo  # noqa E402

from colecciones import Espacios

from utils import (  # noqa E402
    ERRORES,
    array_natural,
    actualizar_presencia,
    attr2dict
)

from servidor import iniciar_servidor  # noqa E402

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
    # debug_guilds=[839277844257570846],
)

# Cargar extensiones por defecto
for ext in cfg.EXT_DEFAULT:
    bot.load_extension(f"{cfg.EXT}.{ext}")


# EVENTOS #####################################################################


@bot.event
async def on_ready():
    print(f"Sesión iniciada como {bot.user} (ID: {bot.user.id})")
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
        await ctx.send(
            ERRORES[error.__class__.__name__].format(**attr2dict(error))
        )
    except Exception as e:
        print(e)  # debug


@bot.event
async def on_application_error(ctx, error):
    print(error)  # debug
    try:
        await ctx.respond(
            ERRORES[error.__class__.__name__].format(**attr2dict(error))
        )
    except Exception as e:
        print(e)  # debug


# EJECUCIÓN ###################################################################

iniciar_servidor()
bot.run(cfg.BOT_TOKEN)

print("<?> Ejecutado: main.py")

# EOF #########################################################################
