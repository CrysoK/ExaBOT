import datetime as dt
from asyncio import sleep
from random import choice
from typing import Optional

from colecciones import A_TODOS, SOLO_A_BOTS, SOLO_A_HUMANOS, Espacios, Saludo
from discord import (
    ApplicationContext,
    AuditLogAction,
    TextChannel,
    User,
    SlashCommandGroup,
)
from discord.ext.commands import Cog
from utils import cnt_bots, cnt_humanos, actualizar_presencia

# UTILIDADES ##################################################################


def reemplazar_claves(texto, miembro, espacio):
    return texto.format(
        mencion=miembro.mention,
        espacio=espacio.name,
        humanos=cnt_humanos([espacio]),
        miembros=espacio.member_count,
        bots=cnt_bots([espacio]),
        usuario=miembro.name,
        miembro=miembro.display_name,
    )


async def saludo_evento(miembro, espacio, tipo_evento):
    config = Espacios.objects(_id=espacio.id).first()
    if not config:
        # El espacio no está registrado, en teoría esto nunca pasaría
        return
    saludos = getattr(config, tipo_evento)
    if not saludos:
        # La función nunca se activó
        return
    # Miembro es un bot?
    if miembro.bot:
        mensajes = filter(
            lambda m: m.tipo == A_TODOS or m.tipo == SOLO_A_BOTS,
            saludos,
        )
    else:
        mensajes = filter(
            lambda m: m.tipo == A_TODOS or m.tipo == SOLO_A_HUMANOS,
            saludos,
        )
    if not mensajes:
        # No hay mensajes para enviar
        return
    # Elige un mensaje aleatorio
    mensaje = choice(list(mensajes))
    canal = espacio.get_channel(mensaje.canal)
    if not canal:
        # No se indicó un canal
        return
    texto = mensaje.texto
    if not texto:
        # No se indicó el contenido del mensaje
        return
    # Se convierten las palabras claves a sus correspondientes valores
    await canal.send(reemplazar_claves(texto, miembro, espacio))


async def saludo_guardar(evento, espacio, tipo, canal, texto):
    config = Espacios.objects(_id=espacio.id).first()
    if not config:
        return False
    saludo = Saludo(canal=canal.id, texto=texto, tipo=tipo)
    getattr(config, evento).append(saludo)
    config.save()
    return True


async def saludo_eliminar(espacio, evento, _id):
    config = Espacios.objects(_id=espacio.id).first()
    if not config:
        return False
    mensajes = getattr(config, evento)
    if not mensajes:
        return False
    del mensajes[_id - 1]
    config.save()
    return True


async def registro_audit(miembro, accion, desde):
    registro = None
    async for r in miembro.guild.audit_logs(
        limit=50,
        action=accion,
        after=desde,
        oldest_first=False,
    ):  # 10 para prevenir falsos positivos (join-kick-join-leave)
        if r.created_at < desde:
            continue
        if r.target.id == miembro.id:
            registro = r
            break
    return registro


# COG #########################################################################


class Registros(Cog, name="Registros"):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_member_join(self, miembro):
        await saludo_evento(miembro, miembro.guild, "entrada")
        await actualizar_presencia(self.bot)

    @Cog.listener()
    async def on_member_remove(self, miembro):
        # Espera a que la expulsión o el ban se registre
        await sleep(0.5)
        # Se busca desde 10 segundos antes
        desde = dt.datetime.utcnow() - dt.timedelta(seconds=10)
        desde = desde.replace(tzinfo=dt.timezone.utc)
        # Se busca la expulsión
        registro = await registro_audit(miembro, AuditLogAction.kick, desde)
        if registro:
            return await saludo_evento(miembro, miembro.guild, "kick")
        # Se busca el ban
        registro = await registro_audit(miembro, AuditLogAction.ban, desde)
        if registro:
            return await saludo_evento(miembro, miembro.guild, "ban")
        # No es expulsión ni ban
        await saludo_evento(miembro, miembro.guild, "salida")
        await actualizar_presencia(self.bot)

    _saludos = SlashCommandGroup(
        "saludos",
        "Mensajes automáticos personalizables. Al indicar más de un mensaje "
        "por evento, se elige uno al azar.",
    )

    "Mensajes automáticos personalizables para cuando alguien entra, sale,"
    "es expulsado o es baneado. Al indicar más de un mensaje por evento, "
    "se elige uno al azar. Puedes definir que el mensaje se envíe para "
    "todos (opción 0), solo para humanos (opción 1) o solo para bots "
    "(opción 2)."

    _entrada = _saludos.create_subgroup(
        "entrada",
        "Añade y elimina mensajes para cuando alguien se une al espacio.",
    )

    _salida = _saludos.create_subgroup(
        "salida",
        "Añade y elimina mensajes para cuando alguien se va del espacio.",
    )

    _kick = _saludos.create_subgroup(
        "expulsión",
        "Añade y elimina mensajes para cuando alguien es expulsado del "
        "espacio.",
    )

    _ban = _saludos.create_subgroup(
        "ban",
        "Añade y elimina mensajes para cuando alguien es baneado del espacio.",
    )

    @_saludos.command(name="listar")
    async def _listar(self, ctx: ApplicationContext, usuario: Optional[User]):
        """
        Lista de todos los mensajes configurados en este espacio. Indica
        cualquier usuario para ver las palabras claves convertidas a sus
        respectivos valores.
        """
        espacio = Espacios.objects(_id=ctx.guild.id).first()
        if not espacio:
            return

        tipo = ["a todos [0]", "solo a humanos [1]", "solo a bots [2]"]
        titulos = [
            "```\nEntrada```\n",
            "```\nSalida```\n",
            "```\nKick```\n",
            "```\nBan```\n",
        ]
        eventos = ["entrada", "salida", "kick", "ban"]

        mensaje = ""
        for i, evento in enumerate(eventos):
            mensaje += titulos[i]
            for i, saludo in enumerate(getattr(espacio, evento)):
                mensaje += (
                    f"`ID {i + 1} | "
                    + f"Responde {tipo[saludo.tipo]} | "
                    + f"Canal` <#{saludo.canal}>\n"
                )
                if usuario:
                    mensaje += reemplazar_claves(
                        saludo.texto, usuario, ctx.guild
                    )
                else:
                    mensaje += saludo.texto
                mensaje += "\n\n"

        await ctx.respond(mensaje)

    @_entrada.command(name="añadir")
    async def _entrada_add(
        self, ctx: ApplicationContext, tipo: int, canal: TextChannel, *, texto
    ):
        if tipo not in [A_TODOS, SOLO_A_HUMANOS, SOLO_A_BOTS]:
            return await ctx.respond(
                "Error: El tipo debe ser 0 (a todos), 1 (solo a humanos) o 2 "
                + "(solo a bots)"
            )
        if await saludo_guardar("entrada", ctx.guild, tipo, canal, texto):
            await ctx.respond("Mensaje añadido correctamente.")
        else:
            await ctx.respond("Error: No se ha podido añadir el mensaje.")

    @_entrada.command(name="eliminar")
    async def _entrada_del(self, ctx: ApplicationContext, _id: int):
        if await saludo_eliminar(ctx.guild, "entrada", _id):
            await ctx.respond("Mensaje eliminado correctamente.")
        else:
            await ctx.respond("Error: No se ha podido eliminar el mensaje.")

    @_salida.command(name="añadir")
    async def _salida_add(
        self, ctx: ApplicationContext, tipo: int, canal: TextChannel, *, texto
    ):
        if tipo not in [A_TODOS, SOLO_A_HUMANOS, SOLO_A_BOTS]:
            return await ctx.respond(
                "Error: El tipo debe ser 0 (a todos), 1 (solo a humanos) o 2 "
                + "(solo a bots)"
            )
        if await saludo_guardar("salida", ctx.guild, tipo, canal, texto):
            await ctx.respond("Mensaje añadido correctamente.")
        else:
            await ctx.respond("Error: No se ha podido añadir el mensaje.")

    @_salida.command(name="eliminar")
    async def _salida_del(self, ctx: ApplicationContext, _id: int):
        if await saludo_eliminar(ctx.guild, "salida", _id):
            await ctx.respond("Mensaje eliminado correctamente.")
        else:
            await ctx.respond("Error: No se ha podido eliminar el mensaje.")

    @_kick.command(name="añadir", aliases=["a"])
    async def _kick_add(
        self, ctx: ApplicationContext, tipo: int, canal: TextChannel, *, texto
    ):
        if tipo not in [A_TODOS, SOLO_A_HUMANOS, SOLO_A_BOTS]:
            return await ctx.respond(
                "Error: El tipo debe ser 0 (a todos), 1 (solo a humanos) o 2 "
                + "(solo a bots)"
            )
        if await saludo_guardar("kick", ctx.guild, tipo, canal, texto):
            await ctx.respond("Mensaje añadido correctamente.")
        else:
            await ctx.respond("Error: No se ha podido añadir el mensaje.")

    @_kick.command(name="eliminar", aliases=["e"])
    async def _kick_del(self, ctx: ApplicationContext, _id: int):
        if await saludo_eliminar(ctx.guild, "kick", _id):
            await ctx.respond("Mensaje eliminado correctamente.")
        else:
            await ctx.respond("Error: No se ha podido eliminar el mensaje.")

    @_ban.command(name="añadir", aliases=["a"])
    async def _ban_add(
        self, ctx: ApplicationContext, tipo: int, canal: TextChannel, *, texto
    ):
        if tipo not in [A_TODOS, SOLO_A_HUMANOS, SOLO_A_BOTS]:
            return await ctx.respond(
                "Error: El tipo debe ser 0 (a todos), 1 (solo a humanos) o 2 "
                + "(solo a bots)"
            )
        if await saludo_guardar("ban", ctx.guild, tipo, canal, texto):
            await ctx.respond("Mensaje añadido correctamente.")
        else:
            await ctx.respond("Error: No se ha podido añadir el mensaje.")

    @_ban.command(name="eliminar", aliases=["e"])
    async def _ban_del(self, ctx: ApplicationContext, _id: int):
        if await saludo_eliminar(ctx.guild, "ban", _id):
            await ctx.respond("Mensaje eliminado correctamente.")
        else:
            await ctx.respond("Error: No se ha podido eliminar el mensaje.")


def setup(bot):
    bot.add_cog(Registros(bot))


print("<?> Ejecutado: Registros.py")
