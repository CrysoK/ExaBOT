import discord as ds
from discord.ext import commands

from utils import son_emojis


from colecciones import Canales, AutoReacciones


class AutoReaccion(commands.Cog, name="AutoReacción"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, mensaje: ds.Message):
        canal = Canales.objects(_id=mensaje.channel.id).first()
        if not canal:
            return
        if not canal.autoreacciones:
            return
        emojis = canal.autoreacciones.reacciones
        for e in emojis:
            await mensaje.add_reaction(e)

    _autoreaccion = ds.SlashCommandGroup(
        "auto-reacción", "Reacciones automáticas a los mensajes de un canal."
    )

    @_autoreaccion.command(name="añadir", ephemeral=True)
    async def _añadir(
        self,
        ctx: ds.ApplicationContext,
        canal: ds.TextChannel,
        emoji: str,
    ):
        """Activar las reacciones automáticas en un canal."""
        if not emoji:
            return await ctx.respond("**Error**: debes indicar un emoji")
        # Si hay algo, se revisa que sean emojis válidos
        if not await son_emojis(ctx, [emoji]):
            return await ctx.respond("**Error**: debes indicar un emoji válido")
        # Si son válidos, se activa la función en el canal indicado
        canal_db = Canales.objects(_id=canal.id).first()
        if not canal_db:
            # si no existe, se crea
            canal_db = Canales(
                _id=canal.id,
                espacio=canal.guild.id,
            )
        if canal_db.autoreacciones:
            canal_db.autoreacciones.reacciones.append(emoji)  # type: ignore
        else:
            canal_db.autoreacciones = AutoReacciones(reacciones=[emoji])
        canal_db.save()
        await ctx.respond(
            f"Desde ahora reaccionaré a todos los mensajes de {canal.mention}"
            + f" con {emoji}."
        )

    @_autoreaccion.command(name="eliminar")
    async def _eliminar(self, ctx: ds.ApplicationContext, canal: ds.TextChannel):
        """
        Desactivar las reacciones automáticas en un canal.
        """
        canal_db = Canales.objects(_id=canal.id).first()
        if not canal_db:
            await ctx.respond(
                "El canal indicado no tiene reacciones automáticas activas."
            )
        canal_db.autoreacciones = None
        canal_db.save()
        await ctx.respond(
            f"Las reacciones automáticas en el canal {canal.mention} "
            + "se desactivaron."
        )


def setup(bot):
    bot.add_cog(AutoReaccion(bot))


print("<?> Ejecutado: auto_reaccion.py")
