import discord as ds
from discord.ext import commands

from utils import array_natural, son_emojis


from colecciones import Canales, AutoReacciones


class AutoReaccion(commands.Cog, name="AutoReaccion"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, mensaje):
        canal = Canales.objects(_id=mensaje.channel.id).first()
        if not canal:
            return
        if not canal.autoreacciones:
            return
        emojis = canal.autoreacciones.reacciones
        for e in emojis:
            await mensaje.add_reaction(e)

    @commands.group(
        name="autoreaccion", aliases=["ar"], invoke_without_command=True
    )
    async def _autoreaccion(self, ctx):
        """
        Reacciones automáticas a los mensajes de un canal.
        """
        await ctx.send(
            "Para reaccionar automáticamente a los mensajes de un canal usa "
            + "`autoreaccion añadir`.\nPara detenerlo, usa "
            + "`autoreaccion eliminar`."
        )

    @_autoreaccion.command(name="añadir", aliases=["a"])
    async def _añadir(self, ctx, canal: ds.TextChannel, *emojis):
        """Activar las reacciones automáticas en un canal."""
        if not emojis:
            return await ctx.send("Error: debes indicar al menos un emoji")
        # Si hay algo, se revisa que sean emojis válidos
        if not await son_emojis(ctx, emojis):
            raise commands.CommandError("Error: debes indicar emojis válidos")
        # Si son válidos, se activa la función en el canal indicado
        canal_db = Canales.objects(_id=canal.id).first()
        if not canal_db:
            # si no existe, se crea
            canal_db = Canales(
                _id=canal.id,
                espacio=canal.guild.id,
            )
        canal_db.autoreacciones = AutoReacciones(reacciones=emojis)
        canal_db.save()
        await ctx.send(
            f"Desde ahora reaccionaré a todos los mensajes de {canal.mention}"
            + f" con {array_natural(emojis)}."
        )

    @_autoreaccion.command(name="eliminar", aliases=["e"])
    async def _eliminar(self, ctx, canal: ds.TextChannel):
        """
        Desactivar las reacciones automáticas en un canal.
        """
        canal_db = Canales.objects(_id=canal.id).first()
        if not canal_db:
            await ctx.send(
                "El canal indicado no tiene reacciones automáticas activas."
            )
        canal_db.autoreacciones = None
        canal_db.save()
        await ctx.send(
            f"Las reacciones automáticas en el canal {canal.mention} "
            + "se desactivaron."
        )


def setup(bot):
    bot.add_cog(AutoReaccion(bot))


print("<?> Ejecutado: AutoReaccion.py")
