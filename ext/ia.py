import discord as ds
from discord.ext import commands

from config import OPENAI_ACCESS_TOKEN

from colecciones import Espacios


from utils.youtube import Video
from utils.chatgpt import ChatGPT

PROMPT_INICIAL_CABECERA = """```
id: 0
tipo: mensaje del sistema
```\n\n"""

PROMPT_INICIAL_POR_DEFECTO = """Quiero que actúes como un bot de Discord \
llamado {bot}.
{bot} puede mantener conversaciones con múltiples usuarios a la vez.
{bot} debe mencionar al usuario con quien interactúa.
Los mensajes recibidos comenzarán con metadatos del mensaje en un bloque de \
código.
{bot} puede usar todas las opciones de formato de Discord.
{bot} debe escapar los caracteres de formato que necesiten aparecer \
textualmente en el mensaje enviado.
{bot} iniciará ahora la conversación con un mensaje del estilo: "Hola, soy X. \
¿En qué puedo ayudarte?".
"""

PROMPT_RESUMEN_YT = """En español, para la siguiente transcripción de un \
video de YouTube:
- ¿Qué se dice concretamente sobre el título ({titulo})?
- ¿El título ({titulo}) es clickbait?
- Escribe un resumen del video.
Transcripción: {texto}
"""


class IA(commands.Cog):
    def __init__(self, bot: ds.Bot):
        self.bot = bot
        self.chatgpt = ChatGPT({"access_token": OPENAI_ACCESS_TOKEN})

    @commands.Cog.listener()
    async def on_message(self, message: ds.Message):
        if message.author.bot or not self.bot.user.mentioned_in(message):
            return
        # Responder si mencionan al bot
        with message.channel.typing():
            # Continúa la conversación
            espacio = Espacios.objects(_id=message.guild.id).first()
            try:
                print(espacio.gpt_conv)
                self.chatgpt.conv_id = espacio.gpt_conv["id"]
                self.msg_cnt = espacio.gpt_conv["msg_cnt"]
            except Exception as e:
                print(e)
                await message.reply(
                    "Algo salió mal. Usa `/chat iniciar` y vuelve a intentarlo"
                )
                return
            # Creación del prompt
            prompt = "```\n"
            if message.reference:
                referenced = await message.channel.fetch_message(
                    message.reference.message_id  # type: ignore
                )
                prompt += (
                    f"id: {self.msg_cnt}\n"
                    + "tipo: mensaje referenciado "
                    + f"por el mensaje {self.msg_cnt + 1}\n"
                    + f"autor: {referenced.author.mention}\n"
                    + f"canal: {referenced.channel.name}\n"  # type: ignore
                    + referenced.created_at.strftime(
                        "enviado: %H:%M %a %d %m %Y (UTC)\n"
                    )
                    + "```\n\n"
                    + f"{referenced.content}\n\n"
                    + "```\n"
                )
                self.msg_cnt += 1
            prompt += (
                f"id: {self.msg_cnt}\n"
                + "tipo: mensaje principal\n"
                + f"autor: {message.author.mention}\n"
                + f"canal: {message.channel.name}\n"  # type: ignore
                + message.created_at.strftime(
                    "enviado: %H:%M %a %d %m %Y (UTC)\n"
                )
                + "```\n\n"
                + f"{message.content}\n"
            )
            self.msg_cnt += 1
            response_list = await self.chatgpt.preguntar(prompt)
            espacio.gpt_conv["msg_cnt"] = self.msg_cnt
            espacio.save()
            for m in response_list:
                await message.channel.send(m)

    _chat = ds.SlashCommandGroup("chat", "Configuración del chat con el bot.")

    @_chat.command(name="iniciar")
    async def _start(self, ctx: ds.ApplicationContext):
        await ctx.defer(invisible=True)
        await ctx.respond("Iniciando...")
        espacio = Espacios.objects(_id=ctx.guild_id).first()
        try:
            # Elimina conv previa
            await self.chatgpt.eliminar_conv(espacio.gpt_conv["id"])
        except Exception as e:
            print(e)
        self.chatgpt.nueva_conv()
        # Cabecera del prompt inicial
        prompt = PROMPT_INICIAL_CABECERA
        try:
            # Prompt inicial en un mensaje
            saved = espacio.gpt_conv["prompt_inicial"]
            channel = await ctx.bot.fetch_channel(saved["channel"])
            msg = await channel.fetch_message(saved["id"])  # type: ignore
            prompt += msg.content
        except Exception as e:
            print(e)
            try:
                # Prompt inicial en un archivo local
                with open("prompt.txt", "r", encoding="utf-8") as f:
                    prompt += f.read()
            except Exception as e:
                print(e)
                # Prompt inicial por defecto
                prompt += PROMPT_INICIAL_POR_DEFECTO
        response_list = await self.chatgpt.preguntar(
            prompt.format(bot=self.bot.user.mention)
        )
        # Guarda la nueva conversación (el id se genera al usar ask)
        self.msg_cnt = 1
        espacio.gpt_conv["id"] = self.chatgpt.conv_id
        espacio.gpt_conv["msg_cnt"] = self.msg_cnt
        espacio.save()

        for m in response_list:
            await ctx.respond(m)

    @_chat.command(name="eliminar_prompt")
    @commands.has_permissions(administrator=True)
    async def _rm_prompt(self, ctx: ds.ApplicationContext):
        espacio = Espacios.objects(_id=ctx.guild_id).first()
        espacio.gpt_conv["prompt_inicial"] = None
        espacio.save()
        await ctx.respond("Prompt inicial eliminado")

    @ds.message_command(name="Prompt inicial")
    @commands.has_permissions(administrator=True)
    async def _set_prompt(self, ctx: ds.ApplicationContext, msg: ds.Message):
        espacio = Espacios.objects(_id=ctx.guild_id).first()
        espacio.gpt_conv["prompt_inicial"] = {
            "id": msg.id,
            "channel": msg.channel.id,
        }
        espacio.save()
        await ctx.respond("Prompt inicial establecido")

    _resumir = ds.SlashCommandGroup("resumir")

    @_resumir.command(name="youtube")
    async def _youtube(self, ctx: ds.ApplicationContext, enlace: str):
        await ctx.defer()
        self.chatgpt.nueva_conv()
        with ctx.typing():
            try:
                video = Video(enlace)
                prompt = PROMPT_RESUMEN_YT.format(
                    titulo=video.titulo,
                    texto=video.transcripcion(),
                )
                response_list = await self.chatgpt.preguntar(prompt)
                for m in response_list:
                    await ctx.respond(m)
            except Exception as e:
                print(e)
                await ctx.respond(e)
        if self.chatgpt.conv_id:
            await self.chatgpt.eliminar_conv(self.chatgpt.conv_id)
        self.chatgpt.nueva_conv()


def setup(bot):
    bot.add_cog(IA(bot))


print("<?> Ejecutado: ia.py")
