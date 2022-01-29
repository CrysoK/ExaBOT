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

# from pymongo import MongoClient  # noqa E402
import mongoengine as mongo  # noqa E402

from colecciones import Espacios  # noqa E402
# fmt: on

# INICIALIZACIÓN I ############################################################

mongo.connect(db="ExaBOT", host=cfg.MONGODB_URI)

# MongoDB
# mongodb = MongoClient(cfg.MONGODB_URI)
# # Database
# db = mongodb["ExaBOT"]
# # Colecciones
# espacios = db["espacios"]
# usuarios = db["usuarios"]


# FUNCIONES ###################################################################


async def get_espacio(_id, nombre="<sin_nombre>"):
    espacio = Espacios.objects(id=_id).first()
    if espacio is None:
        espacio = Espacios(id=_id).save()
        print(
            f"Espacio {nombre} (ID: {_id}) " + "no encontrado. Se ha creado."
        )
    print(espacio)
    return espacio


async def get_prefix(bot, message):
    """
    Retorna el prefijo del servidor con el id indicado.
    """
    _id = message.guild.id
    espacio = await get_espacio(_id, message.guild.name)
    print(espacio.prefix)
    return espacio.prefix


async def del_prefix(message, prefix):
    _id = message.guild.id
    espacio = await get_espacio(_id, message.guild.name)
    if len(espacio.prefix) > 1:
        espacio.prefix.remove(prefix)
        espacio.save()
    else:
        await message.channel.send(
            "Error. El bot debe tener al menos un prefijo."
        )


async def add_prefix(message, prefix):
    _id = message.guild.id
    espacio = await get_espacio(_id, message.guild.name)
    espacio.prefix.append(prefix)
    espacio.save()


async def actualizar_presencia():
    total = 0
    for guild in bot.guilds:
        total += len([m for m in guild.members if not m.bot])
    await bot.change_presence(
        activity=ds.Activity(
            type=ds.ActivityType.watching,
            name=f"a {total} humanos",
        ),
    )


# INICIALIZACIÓN II ###########################################################

intents = ds.Intents.all()

bot = commands.Bot(command_prefix=get_prefix, intents=intents)

# Cargar extensiones por defecto
for ext in cfg.EXT_DEFAULT:
    bot.load_extension(f"{cfg.EXT}.{ext}")


# EVENTOS #####################################################################


@bot.event
async def on_ready():
    print(f"Sesión iniciada como {bot.user} (ID: {bot.user.id})")
    await actualizar_presencia()


@bot.event
async def on_message(message):

    print(f"{message.author} en {message.channel}: {message.content}")

    # Reacciones
    if message.channel.id == 924772189507555338:
        await message.add_reaction("👍")
        await message.add_reaction("👎")

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
            res += f"Mis prefijos son `{prefix}`"
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
    await ctx.send(error)


# COMANDOS ####################################################################


@bot.command(name="addprefix")
@commands.has_guild_permissions(administrator=True)
async def _addprefix(ctx, prefix):
    await add_prefix(ctx, prefix)
    await ctx.send(f"Prefijo `{prefix}` añadido")


@bot.command(name="delprefix")
@commands.has_guild_permissions(administrator=True)
async def _delprefix(ctx, prefix):
    await del_prefix(ctx, prefix)
    await ctx.send("Prefijo eliminado")


# ERRORES #####################################################################


# EJECUCIÓN ###################################################################


bot.run(cfg.BOT_TOKEN)

print("<?> Ejecutado: main.py")

# EOF #########################################################################
