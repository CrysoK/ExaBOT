import discord as ds
from discord.ext import commands


class Otros(commands.Cog, name="Otros"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        pass

    @commands.command()
    async def dividir(self, ctx, left: int, right: int):
        """Divide dos números cualquiera."""
        res = left / right
        await ctx.send(res)

    @commands.command(rest_is_raw=True)
    async def repetir(self, ctx, *, arg):
        """Repite una cadena de texto."""
        await ctx.send(arg)

    @commands.command(name="hola")
    async def _hola(self, ctx, *, member: ds.Member = None):
        """Te saludo"""
        member = member or ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send(f"Hola {member.mention}")
        else:
            await ctx.send(f"Hola {member.mention}, de nuevo.")
        self._last_member = member

    @dividir.error
    async def div_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Para dividir necesitas dos números")
        if isinstance(error, ZeroDivisionError):
            await ctx.send("No se puede dividir entre 0")


def setup(bot):
    bot.add_cog(Otros(bot))


print("<?> Ejecutado: Otros.py")
