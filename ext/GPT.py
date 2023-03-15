import discord as ds
from discord.ext import commands

from revChatGPT.V1 import AsyncChatbot
import config as cfg


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
                "email": cfg.OPENAI_EMAIL,
                "password": cfg.OPENAI_PASSWORD,
            }
        )
        self.msgid = 1

    async def ask(self, message: str) -> list[str]:
        print(f"[Prompt] {message}")
        raw_response = ""
        async for r in self.chatbot.ask(message):
            raw_response = r["message"]
        print(f"[Respuesta] {raw_response}")
        return split_response(raw_response, char_limit=1900)

    async def send_list(self, channel, message_list):
        for message in message_list:
            await channel.send(message)

    async def start_prompt(self):
        # Enviar prompt, si existe. Lo ideal sería indicar el ID de un mensaje
        # que haga de prompt inicial + un canal donde vaya la respuesta
        with open("prompt.txt", "r", encoding="utf-8") as f:
            prompt = f.read()
        channel = self.bot.get_channel(839288466931580948)
        response_list = await self.ask(
            prompt.format(bot=self.bot.user.mention)
        )
        await self.send_list(channel, response_list)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.start_prompt()

    @commands.Cog.listener()
    async def on_message(self, message: ds.Message):
        if message.author.bot or not self.bot.user.mentioned_in(message):
            return
        # Responder si mencionan al bot
        with message.channel.typing():
            prompt = "```\n"
            if message.reference:
                referenced = await message.channel.fetch_message(
                    message.reference.message_id
                )
                prompt += (
                    f"id: {self.msgid}\n"
                    + "tipo: mensaje referenciado "
                    + f"por el mensaje {self.msgid + 1}\n"
                    + f"autor: {referenced.author.mention}\n"
                    + f"canal: {referenced.channel.name}\n"
                    + referenced.created_at.strftime(
                        "enviado: %H:%M %a %d %m %Y (UTC)\n"
                    )
                    + "```\n\n"
                    + f"{referenced.content}\n\n"
                    + "```\n"
                )
                self.msgid += 1
            prompt += (
                f"id: {self.msgid}\n"
                + "tipo: mensaje principal\n"
                + f"autor: {message.author.mention}\n"
                + f"canal: {message.channel.name}\n"
                + message.created_at.strftime(
                    "enviado: %H:%M %a %d %m %Y (UTC)\n"
                )
                + "```\n\n"
                + f"{message.content}\n"
            )
            self.msgid += 1
            response_list = await self.ask(prompt)
            await self.send_list(message.channel, response_list)

    _chat = ds.SlashCommandGroup("chat", "Configuración del chat con el bot.")

    @_chat.command(name="reiniciar")
    async def _reset(self, ctx: ds.ApplicationContext):
        # await self.chatbot.delete_conversation(self.chatid)
        self.chatbot.reset_chat()
        await ctx.respond('"Memoria" reiniciada')
        await self.start_prompt()


def setup(bot):
    bot.add_cog(GPT(bot))


print("<?> Ejecutado: GPT.py")
