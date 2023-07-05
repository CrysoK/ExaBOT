import discord as ds
from discord.ext import commands

from revChatGPT.V1 import AsyncChatbot
from colecciones import Espacios
import config as cfg
from utils.youtube import Video

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

PROMPT_RESUMEN_YT = """Para la siguiente transcripción automática de un \
video de YouTube:
- ¿Qué se dice el video sobre el título ({titulo})?
- Escribe un resumen detallado del video.
Transcripción: {texto}
"""


# Split the response into smaller chunks of no more than 1900
# characters each(Discord limit is 2000 per chunk)
def split_response(response, char_limit) -> list[str]:
    result = []
    if "```" not in response:
        response_chunks = [
            response[i : i + char_limit]
            for i in range(0, len(response), char_limit)
        ]
        for chunk in response_chunks:
            result.append(chunk)
        return result
    # Split the response if the code block exists
    parts = response.split("```")
    for i in range(len(parts)):
        if i % 2 == 0:  # indices that are even are not code blocks
            result.append(parts[i])
        else:  # Odd-numbered parts are code blocks
            code_block = parts[i].split("\n")
            formatted_code_block = ""
            for line in code_block:
                while len(line) > char_limit:
                    # Split the line at the 50th character
                    formatted_code_block += line[:char_limit] + "\n"
                    line = line[char_limit:]
                formatted_code_block += (
                    line + "\n"
                )  # Add the line and separate with new line

            # Send the code block in a separate message
            if len(formatted_code_block) > char_limit + 100:
                code_block_chunks = [
                    formatted_code_block[i : i + char_limit]
                    for i in range(0, len(formatted_code_block), char_limit)
                ]
                for chunk in code_block_chunks:
                    result.append(f"```{chunk}```")
            else:
                result.append(f"```{formatted_code_block}```")
    return result


class GPT(commands.Cog):
    def __init__(self, bot: ds.Bot):
        self.bot = bot
        self.chatbot = AsyncChatbot(
            config={
                "access_token": cfg.OPENAI_ACCESS_TOKEN,
            }
        )

    async def ask(self, message: str) -> list[str]:
        print(f"[Prompt] {message}")
        raw_response = ""
        async for r in self.chatbot.ask(message):
            raw_response = r["message"]
        print(f"[Respuesta] {raw_response}")
        return split_response(raw_response, char_limit=1900)

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
                self.chatbot.conversation_id = espacio.gpt_conv["id"]
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
            response_list = await self.ask(prompt)
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
            await self.chatbot.delete_conversation(espacio.gpt_conv["id"])
        except Exception as e:
            print(e)
        self.chatbot.reset_chat()
        # Cabecera del prompt inicial
        prompt = PROMPT_INICIAL_CABECERA
        try:
            # Prompt inicial en un mensaje
            prompt += (
                await ctx.fetch_message(espacio.gpt_conv["prompt_inicial_id"])
            ).content
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
        response_list = await self.ask(
            prompt.format(bot=self.bot.user.mention)
        )
        # Guarda la nueva conversación (el id se genera al usar ask)
        self.msg_cnt = 1
        espacio.gpt_conv["id"] = self.chatbot.conversation_id
        espacio.gpt_conv["msg_cnt"] = self.msg_cnt
        espacio.save()

        for m in response_list:
            await ctx.respond(m)

    @_chat.command(name="eliminar_prompt")
    @commands.has_permissions(administrator=True)
    async def _rm_prompt(self, ctx: ds.ApplicationContext):
        espacio = Espacios.objects(_id=ctx.guild_id).first()
        espacio.gpt_conv["prompt_inicial_id"] = None
        espacio.save()
        await ctx.respond("Prompt inicial eliminado")

    @ds.message_command(name="Prompt inicial")
    @commands.has_permissions(administrator=True)
    async def _set_prompt(self, ctx: ds.ApplicationContext, msg: ds.Message):
        espacio = Espacios.objects(_id=ctx.guild_id).first()
        espacio.gpt_conv["prompt_inicial_id"] = msg.id
        espacio.save()
        await ctx.respond("Prompt inicial establecido")

    _resumir = ds.SlashCommandGroup("resumir")

    @_resumir.command(name="youtube")
    async def _youtube(self, ctx: ds.ApplicationContext, enlace: str):
        await ctx.defer()
        self.chatbot.reset_chat()
        with ctx.typing():
            try:
                video = Video(enlace)
                prompt = PROMPT_RESUMEN_YT.format(
                    titulo=video.titulo,
                    texto=video.transcripcion(),
                )
                response_list = await self.ask(prompt)
                for m in response_list:
                    await ctx.respond(m)
            except Exception as e:
                print(e)
                await ctx.respond(f"Los idiomas disponibles son: {e}")
        if self.chatbot.conversation_id:
            await self.chatbot.delete_conversation(
                self.chatbot.conversation_id
            )
        self.chatbot.reset_chat()


def setup(bot):
    bot.add_cog(GPT(bot))


print("<?> Ejecutado: GPT.py")
