import os
from discord.ext import commands
import config as cfg


class Owner(commands.Cog, name="Owner"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        pass

    @commands.command(name="addext")
    @commands.is_owner()
    async def _addext(self, ctx, ext):
        self.bot.load_extension(f"{cfg.EXT}.{ext}")
        await ctx.send(f"Comando `{ext}` cargado")

    @commands.command(name="reload")
    @commands.is_owner()
    async def _reloadext(self, ctx):
        """
        Recarga todas las extensiones
        """
        for ext in os.listdir(f"./{cfg.EXT}"):
            if ext.endswith(".py"):
                self.bot.reload_extension(f"{cfg.EXT}.{ext[:-3]}")
        await ctx.send("Extensiones recargadas")

    @commands.command(name="delext")
    @commands.is_owner()
    async def _delext(self, ctx, ext):
        self.bot.unload_extension(f"{cfg.EXT}.{ext}")
        await ctx.send(f"Extensión {ext} desactivada")

    @commands.command(name="eval")
    @commands.is_owner()
    async def _eval(self, ctx, *, code):
        await ctx.send(eval(code))

    @commands.command(name="exec")
    @commands.is_owner()
    async def _exec(self, ctx, *, code):
        await ctx.send(exec(code))


def setup(bot):
    bot.add_cog(Owner(bot))


print("<?> Ejecutado: Owner.py")
