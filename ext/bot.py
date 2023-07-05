import os
import config as cfg
import discord as ds
from discord.ext import commands


class Bot(commands.Cog, name="Bot"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # @commands.command(name="sync")
    # @commands.is_owner()
    # async def _sync(
    #     self,
    #     ctx: commands.Context,
    #     guild: ds.Guild | None,
    # ):
    #     synced = await self.bot.tree.sync(guild=guild)
    #     await ctx.send(f"Comandos sincronizados: {len(synced)}")

    _ext = ds.SlashCommandGroup("ext", "Controla las extensiones (solo owner)")

    @_ext.command(name="recargar")
    @commands.is_owner()
    async def _ext_recargar(self, ctx: ds.ApplicationContext):
        """
        Recarga todas las extensiones (solo owner).
        """
        for ext in os.listdir(f"./{cfg.EXT}"):
            if ext.endswith(".py"):
                self.bot.reload_extension(f"{cfg.EXT}.{ext[:-3]}")
        await ctx.respond("Extensiones recargadas")

    @_ext.command(name="añadir")
    @commands.is_owner()
    async def _ext_add(self, ctx: ds.ApplicationContext, extensión: str):
        """
        Cargar una extensión (solo owner).
        """
        self.bot.load_extension(f"{cfg.EXT}.{extensión}")
        await ctx.respond(f"Comando `{extensión}` cargado")

    @_ext.command(name="eliminar")
    @commands.is_owner()
    async def _ext_del(self, ctx: ds.ApplicationContext, extensión: str):
        """
        Remueve una extensión (solo owner).
        """
        self.bot.unload_extension(f"{cfg.EXT}.{extensión}")
        await ctx.respond(f"Extensión {extensión} desactivada")

    _py = ds.SlashCommandGroup(
        "python", "Utiliza funciones de Python (solo owner)."
    )

    @_py.command(name="eval")
    @commands.is_owner()
    async def _py_eval(self, ctx: ds.ApplicationContext, código: str):
        """
        Python `eval` (solo owner).
        """
        await ctx.respond(eval(código))

    @_py.command(name="exec")
    @commands.is_owner()
    async def _py_exec(self, ctx: ds.ApplicationContext, código: str):
        """
        Python `exec` (solo owner).
        """
        await ctx.respond(exec(código))


def setup(bot):
    bot.add_cog(Bot(bot))


print("<?> Ejecutado: bot.py")
