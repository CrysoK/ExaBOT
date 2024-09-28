from typing import Optional
import discord as ds
from discord.ext import commands
from discord.utils import get as ds_get
from utils import array_natural

import logging

logger = logging.getLogger(__name__)


class Otros(commands.Cog, name="Otros"):
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
        materia: str,
        carreras: str,
        categoria: Optional[ds.CategoryChannel],
    ):
        """Crea un foro para una materia y los posts por defecto.
        `carreras` debe ser una lista de roles separados por coma.
        """
        await ctx.defer()
        carreras_l = [
            ds_get(ctx.guild.roles, name=x)
            for x in [x.strip() for x in carreras.split(",")]
        ]
        permisos = {}
        if not categoria or len(carreras_l) > 1:
            # Se deben establecer permisos particulares para el canal
            permisos[ctx.guild.default_role] = ds.PermissionOverwrite(
                read_messages=False
            )
            for c in carreras_l:
                permisos[c] = ds.PermissionOverwrite(read_messages=True)
        foro = await ctx.guild.create_forum_channel(
            name=materia,
            category=categoria,
            overwrites=permisos,  # type: ignore
        )
        await foro.edit(default_auto_archive_duration=10080)
        await foro.create_thread("Finales", content="_ _")
        await foro.create_thread("Parciales", content="_ _")
        await foro.create_thread("Recursos", content="_ _")
        await foro.create_thread("Medios", content="_ _")
        await foro.create_thread("Chat", content="_ _")
        num = "s" if len(carreras_l) > 1 else ""
        await ctx.respond(
            f"Se creó el foro para la materia `{materia}` de la{num} carrera{num} "
            + f"{array_natural(carreras_l, formato='**')}."
        )

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


def setup(bot):
    bot.add_cog(Otros(bot))


logger.info("Ejecutado: otros.py")
