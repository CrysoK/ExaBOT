from discord.ext import commands


class Otros(commands.Cog, name="Otros"):
    def __init__(self, bot):
        self.bot = bot

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

    @dividir.error
    async def div_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Para dividir necesitas dos números")
        if isinstance(error, ZeroDivisionError):
            await ctx.send("No se puede dividir entre 0")


def setup(bot):
    bot.add_cog(Otros(bot))


print("<?> Ejecutado: Otros.py")
