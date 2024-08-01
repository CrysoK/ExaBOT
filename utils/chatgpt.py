from typing import List
from revChatGPT.V1 import AsyncChatbot


class ChatGPT:
    def __init__(self, config):
        self._client = AsyncChatbot(config=config)
        self.conv_id = self._client.conversation_id

    async def preguntar(self, mensaje: str) -> List[str]:
        print(f"[Prompt] {mensaje}")
        respuesta = ""
        async for r in self._client.ask(mensaje):
            respuesta = r["message"]
        print(f"[Respuesta] {respuesta}")
        self.conv_id = self._client.conversation_id
        return split_response(respuesta, char_limit=1900)

    async def eliminar_conv(self, conv_id):
        await self._client.delete_conversation(conv_id)

    def nueva_conv(self):
        self._client.reset_chat()


# Split the response into smaller chunks of no more than 1900
# characters each(Discord limit is 2000 per chunk)
def split_response(response, char_limit) -> List[str]:
    """
    Split the response into smaller chunks of no more than char_limit characters each.
    If the response contains a code block, split it into chunks of no more than char_limit characters.
    Return a list of response chunks.
    """
    result = []
    if response is None:
        raise ValueError("Response cannot be None")
    if char_limit is None:
        raise ValueError("Char limit cannot be None")
    if not isinstance(char_limit, int):
        raise TypeError("Char limit must be an integer")
    if "```" not in response:
        response_chunks = [
            response[i : i + char_limit] for i in range(0, len(response), char_limit)
        ]
        for chunk in response_chunks:
            result.append(chunk)
        return result
    # Split the response if the code block exists
    parts = response.split("```")
    for i, part in enumerate(parts):
        if i % 2 == 0:  # indices that are even are not code blocks
            result.append(part)
        else:  # Odd-numbered parts are code blocks
            code_block = part.split("\n")
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
