# DEPENDENCIAS ################################################################

# fmt: off
import logging
logging.basicConfig(level=logging.INFO)

import sys  # noqa E402
sys.path.append("config.py")

import discord as ds  # noqa E402
from discord.ext import commands  # noqa E402

from dotenv import load_dotenv  # noqa E402
load_dotenv(override=True)

import config as cfg  # noqa E402

import mongoengine as mongo  # noqa E402

from utils import (  # noqa E402
    ERRORES,
    get_prefix,
    array_natural,
    cambiar_presencia,
    attr2dict
)
# fmt: on

# INICIALIZACIÓN ##############################################################


# Comando de ayuda personalizado que hereda del comando por defecto.
class Ayuda(commands.DefaultHelpCommand):
    pass


# Conexión a la base de datos.
mongo.connect(db="ExaBOT", host=cfg.MONGODB_URI)

# Intents de Discord para el bot.
intents = ds.Intents.all()


bot = commands.Bot(
    command_prefix=get_prefix,
    intents=intents,
    help_command=Ayuda(
        commands_heading="Comandos",
        aliases_heading="Alias",
        no_category="Sin categoría",
        command_attrs={
            "name": "ayuda",
            "aliases": ["help", "h", "comandos", "cmds", "cmd"],
        },
    ),
)


# Cargar extensiones por defecto
for ext in cfg.EXT_DEFAULT:
    bot.load_extension(f"{cfg.EXT}.{ext}")


# EVENTOS #####################################################################


@bot.event
async def on_ready():
    print(f"Sesión iniciada como {bot.user} (ID: {bot.user.id})")
    await cambiar_presencia(bot)


@bot.event
async def on_message(message):

    print(f"{message.author} en {message.channel}: {message.content}")

    # Mención al bot
    if (
        message.content == f"<@{bot.user.id}>"
        or message.content == f"<@!{bot.user.id}>"
    ):
        prefix = await get_prefix(bot, message)
        res = "Hola. "
        if len(prefix) == 1:
            res += f"Mi prefijo es `{prefix[0]}`"
        else:
            res += f"Mis prefijos son {array_natural(prefix, formato='`')}."

        await message.channel.send(res)

    # Continuar con los comandos definidos
    await bot.process_commands(message)


@bot.event
async def on_guild_remove(guild):
    """
    ¿Debería eliminar todos los datos de la base de datos o eso debería ser un
    comando (por ejemplo, `restablecer_bot`)?
    """
    pass


@bot.event
async def on_command_error(ctx, error):
    # TODO: Traducir todos los errores.
    # await ctx.send(error)
    await ctx.send(
        ERRORES[error.__class__.__name__].format(**attr2dict(error))
    )


# EJECUCIÓN ###################################################################


bot.run(cfg.BOT_TOKEN)

print("<?> Ejecutado: main.py")

# EOF #########################################################################
