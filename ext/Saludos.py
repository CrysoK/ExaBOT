import discord as ds
from discord.ext import commands


class Saludos(commands.Cog, name="Saludos"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f"Bienvenido {member.mention}.")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        pass

    @commands.command(name="hola")
    async def _hola(self, ctx, *, member: ds.Member = None):
        """Says hello"""
        member = member or ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send(f"Hola {member.mention}")
        else:
            await ctx.send(f"Hola {member.mention}, de nuevo.")
        self._last_member = member


def setup(bot):
    bot.add_cog(Saludos(bot))


print("<?> Ejecutado: Saludos.py")
