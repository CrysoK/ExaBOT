import discord as ds
from discord.ext import commands


class Otros(commands.Cog, name="Otros"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        pass

    @ds.slash_command()
    async def dividir(self, ctx: ds.ApplicationContext, a: int, b: int):
        """Divide dos números cualquiera."""
        res = a / b
        await ctx.respond(res)

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

    @dividir.error
    async def div_error(self, ctx, error):  # esto sigue funcionando con slash?
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Para dividir necesitas dos números")
        if isinstance(error, ZeroDivisionError):
            await ctx.send("No se puede dividir entre 0")


def setup(bot):
    bot.add_cog(Otros(bot))


print("<?> Ejecutado: Otros.py")
