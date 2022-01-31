import os
import config as cfg
from discord.ext import commands
from utils import del_prefix, add_prefix


class Bot(commands.Cog, name="Bot"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        pass

    @commands.group(name="ext", invoke_without_command=True)
    async def _ext(self, ctx):
        """
        Controla las extensiones (solo owner)
        """
        pass

    @_ext.command(name="recargar", aliases=["r"])
    @commands.is_owner()
    async def _ext_recargar(self, ctx):
        """
        Recarga todas las extensiones (solo owner).
        """
        for ext in os.listdir(f"./{cfg.EXT}"):
            if ext.endswith(".py"):
                self.bot.reload_extension(f"{cfg.EXT}.{ext[:-3]}")
        await ctx.send("Extensiones recargadas")

    @_ext.command(name="añadir", aliases=["a"])
    @commands.is_owner()
    async def _ext_add(self, ctx, ext):
        """
        Cargar una extensión (solo owner).
        """
        self.bot.load_extension(f"{cfg.EXT}.{ext}")
        await ctx.send(f"Comando `{ext}` cargado")

    @_ext.command(name="eliminar", aliases=["e"])
    @commands.is_owner()
    async def _ext_del(self, ctx, ext):
        """
        Remueve una extensión (solo owner).
        """
        self.bot.unload_extension(f"{cfg.EXT}.{ext}")
        await ctx.send(f"Extensión {ext} desactivada")

    @commands.group(name="python", aliases=["py"], invoke_without_command=True)
    async def _py(self, ctx):
        """
        Utiliza funciones de Python (solo owner).
        """
        pass

    @_py.command(name="eval")
    @commands.is_owner()
    async def _py_eval(self, ctx, *, code):
        """
        Python `eval` (solo owner).
        """
        await ctx.send(eval(code))

    @_py.command(name="exec")
    @commands.is_owner()
    async def _py_exec(self, ctx, *, code):
        """
        Python `exec` (solo owner).
        """
        await ctx.send(exec(code))

    @commands.group(name="prefix", aliases=["p"], invoke_without_command=True)
    @commands.has_guild_permissions(manage_guild=True)
    async def _prefix(self, ctx):
        """
        Controla los prefijos del bot (necesario: gestionar servidor).
        """
        pass

    @_prefix.command(name="añadir", aliases=["a"])
    @commands.has_guild_permissions(manage_guild=True)
    async def _prefix_add(self, ctx, prefix):
        """
        Añade un prefijo al bot.
        """
        await add_prefix(ctx, prefix)
        await ctx.send(f"Prefijo `{prefix}` añadido")

    @_prefix.command(name="eliminar", aliases=["e"])
    @commands.has_guild_permissions(manage_guild=True)
    async def _prefix_del(self, ctx, prefix):
        """
        Elimina un prefijo del bot.
        """
        await del_prefix(ctx, prefix)
        await ctx.send(f"Prefijo `{prefix}` eliminado")


def setup(bot):
    bot.add_cog(Bot(bot))


print("<?> Ejecutado: Bot.py")
