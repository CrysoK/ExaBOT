import discord as ds
from discord.ext import commands
from colecciones import Espacios

from emoji import emoji_count

import logging

logger = logging.getLogger(__name__)


async def actualizar_presencia(bot):
    total = cnt_humanos(bot.guilds)
    await bot.change_presence(
        activity=ds.Activity(
            type=ds.ActivityType.watching,
            name=f"a {total} humanos",
        )
    )


def array_natural(array, formato=""):
    """
    Devuelve una representación en lenguaje natural de un array, ejemplo: `"1,
    2 y 3"`. `formato` puede ser, por ejemplo, `"**"` para que cada elemento
    salga en negrita.
    """
    if not array:
        return ""
    f = formato
    array_f = [f"{formato}{elem}{formato}" for elem in array]
    if len(array_f) == 1:
        return array_f[0]
    else:
        return ", ".join(array_f[:-1]) + " y " + array_f[-1]


async def son_emojis(ctx, emojis):
    """
    Validación de una lista de emojis
    """
    for e in emojis:
        # Emoji UNICODE o alias (?)
        if emoji_count(e) == 1:
            continue
        # Discord emoji (personalizados)
        try:
            await commands.EmojiConverter().convert(ctx, e)
            continue
        except commands.EmojiNotFound:
            # Discord partial emoji (personalizados) [es necesario?]
            try:
                await commands.PartialEmojiConverter().convert(ctx, e)
                continue
            except commands.PartialEmojiConversionFailure:
                return False
    return True


async def get_espacio(_id, nombre="<sin_nombre>"):
    espacio = Espacios.objects(_id=_id).first()
    if espacio is None:
        espacio = Espacios(_id=_id).save()
        logger.info(f"Espacio {nombre} (ID: {_id}) " + "no encontrado. Se ha creado.")
    return espacio


def cnt_humanos(guilds):
    total = 0
    for g in guilds:
        total += len([m for m in g.members if not m.bot])
    return total


def cnt_bots(guilds):
    total = 0
    for g in guilds:
        total += len([m for m in g.members if m.bot])
    return total


# Devuelve un diccionario con todos los atributos de dir() y sus valores
def attr2dict(obj):
    ret = {}
    for a in dir(obj):
        ret[a] = getattr(obj, a)
    return ret


# Traducción de los mensajes de errores de Pycord.
ERRORES = {
    # # DiscordException
    "CommandError": "CommandError: {args[0]}",
    "ExtensionError": "La extensión {name!r} tuvo un error.",
    # # # CommandError
    "ConversionError": "ConversionError: {args[0]}",
    "UserInputError": "UserInputError: {args[0]}",
    "CommandNotFound": "CommandNotFound: {args[0]}",
    "CheckFailure": "CheckFailure: {args[0]}",
    "DisabledCommand": "DisabledCommand: {args[0]}",
    "CommandInvokeError": "El comando elevó una excepción: "
    + "{original.__class__.name}: {original}",
    "CommandOnCooldown": "Demasiado rápido. Debes esperar "
    + "{retry_after:.2f} segundos.",
    # fmt debe definirse
    "MaxConcurrencyReached": "Mucha gente usando este comando. Solo pueden "
    + "usarlo {fmt} a la vez.",
    # # # # UserInputError
    "MissingRequiredArgument": "No se indicó el argumento requerido "
    + "`{param.name}`.",
    "TooManyArguments": "TooManyArguments: {args[0]}",
    # fmt debe definirse
    "BadArgument": "BadArgument: {args[0]}",
    "BadUnionArgument": "No se pudo convertir {param} a {fmt}.",
    "ArgumentParsingError": "ArgumentParsingError: {args[0]}",
    # # # # # BadArgument
    "MemberNotFound": 'Miembro "{argument}" no encontrado.',
    "GuildNotFound": 'Espacio "{argument}" no encontrado.',
    "UserNotFound": 'Usuario "{argument}" no encontrado.',
    "MessageNotFound": 'Mensaje "{argument}" no encontrado.',
    "ChannelNotReadable": "No se pueden leer los mensajes de " + "{argument.mention}.",
    "ChannelNotFound": 'Canal "{argument}" no encontrado.',
    "BadColourArgument": 'El color "{argument}" es inválido.',
    "RoleNotFound": 'Rol "{argument}" no encontrado.',
    "BadInviteArgument": "La invitación es inválida o expiró.",
    "EmojiNotFound": 'Emoji "{argument}" no encontrado.',
    "PartialEmojiConversionFailure": 'No se pudo convertir "{argument}" ha '
    + "un PartialEmoji.",
    "BadBoolArgument": "{argument} no es una opción booleana reconocida.",
    # # # # # ArgumentParsingError
    "UnexpectedQuoteError": "Comillas inesperadas ({quote!r}) en una cadena "
    + "sin comillas.",
    "InvalidEndOfQuotedStringError": "Se esperaba un espacio después de las "
    + "comillas de cierre pero se encontró {char}",
    "ExpectedClosingQuoteError": "Se esperaba {close_quote} al final.",
    # # # # CheckFailure
    "CheckAnyFailure": "No tienes permisos para ejecutar este comando.",
    "PrivateMessageOnly": "Este comando solo puede ser usado en mensajes "
    + "privados.",
    "NoPrivateMessage": "Este comando no puede ser usado en mensajes " + "privados.",
    "NotOwner": "NotOwner: {args[0]}",
    "MissingRole": "Se requiere el rol {missing_role} para ejecutar este " + "comando.",
    "BotMissingRole": "El bot requiere el rol {missing_rol} para ejecutar " + "comando",
    # fmt debe definirse
    "MissingAnyRole": "Te falta al menos uno de los roles requeridos: {fmt}.",
    # fmt debe definirse
    "BotMissingAnyRole": "Al bot le falta al menos uno de los roles "
    + "requeridos: {fmt}.",
    "NSFWChannelRequired": "El canal {channel} debe ser NSFW para ejecutar"
    + " este comando",
    # fmt debe definirse
    "MissingPermissions": "Te faltan los permisos {fmt} para ejecutar este "
    + "comando.",
    "BotMissingPermissions": "El bot requiere los permisos {fmt} para ejecutar"
    + "este comando",
    # # # ExtensionError
    "ExtensionAlreadyLoaded": "La extensión {name!r} ya está cargada.",
    "ExtensionNotLoaded": "La extensión {name!r} no ha sido cargada.",
    "NoEntryPointError": "La extensión {name!r} no tiene una función 'setup'.",
    "ExtensionFailed": "La extensión {name!r} elevó un error: "
    + "{original.__class__.name}: {original}.",
    "ExtensionNotFound": "La extensión {name} no se encontró.",
    # # ClientException
    # type_ debe definirse
    "CommandRegistrationError": "El {type_} {name} ya existe.",
}
