from discord.ext import commands


class Registros(commands.Cog, name="Registros"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f"Bienvenido {member.mention}.")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        pass


def setup(bot):
    bot.add_cog(Registros(bot))


print("<?> Ejecutado: Registros.py")
