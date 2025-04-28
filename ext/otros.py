from typing import Optional
import discord as ds
from discord.ext import commands
from discord.utils import get as ds_get
from utils import array_natural

import logging

logger = logging.getLogger(__name__)


class Otros(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        pass

    @ds.slash_command()
    @commands.has_permissions(manage_channels=True)
    async def crear_materia(
        self,
        ctx: ds.ApplicationContext,
        foro: ds.ForumChannel,
        nombre: str,
        otros_nombres: str,
    ):
        """Crea una materia (post) dentro de un foro.
        Los nombres alternativos van en el cuerpo del post.
        """
        await ctx.defer()
        await foro.create_thread(nombre, content=otros_nombres)
        await ctx.respond(f"Se creó la materia {nombre} en el foro {foro}")

    @ds.slash_command()
    async def dividir(self, ctx: ds.ApplicationContext, a: int, b: int):
        """Divide dos números cualquiera."""
        res = a / b
        await ctx.respond(res)

    @dividir.error
    async def div_error(self, ctx, error):  # esto sigue funcionando con slash?
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Para dividir necesitas dos números")
        if isinstance(error, ZeroDivisionError):
            await ctx.send("No se puede dividir entre 0")

    @ds.slash_command()
    async def repetir(self, ctx: ds.ApplicationContext, texto):
        """Repite una cadena de texto."""
        await ctx.respond(texto)

    @ds.slash_command(name="hola")
    async def _hola(
        self,
        ctx: ds.ApplicationContext,
        miembro: ds.Option(ds.Member, default=None),  # type: ignore
    ):
        """Saludo a alguien"""
        miembro = miembro or ctx.author
        if self._last_member is None or self._last_member.id != miembro.id:
            await ctx.respond(f"Hola {miembro.mention}")
        else:
            await ctx.respond(f"Hola {miembro.mention}, de nuevo.")
        self._last_member = miembro

    @ds.slash_command()
    @commands.has_permissions(manage_messages=True)
    async def editar_mensaje(
        self,
        ctx: ds.ApplicationContext,
        message_id: str,
        nuevo_texto: str,
    ):
        """Edita un mensaje enviado por el bot."""
        try:
            message = await ctx.channel.fetch_message(int(message_id))
            await message.edit(content=nuevo_texto)
            await ctx.respond(f"Mensaje editado: {message_id}")
        except ds.NotFound:
            await ctx.respond(f"No se encontró el mensaje con ID: {message_id}")
        except ds.Forbidden:
            await ctx.respond("No tengo permisos para editar este mensaje.")
        except ValueError:
            await ctx.respond("ID de mensaje inválido.")


def setup(bot):
    bot.add_cog(Otros(bot))


logger.info("Ejecutado: otros.py")
