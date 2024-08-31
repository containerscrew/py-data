import asyncio
from ollama import AsyncClient


async def chat(question):
    """
    Stream a chat from Llama using the AsyncClient.
    """
    message = {
        "role": "user",
        "content": question,
    }

    async for part in await AsyncClient(host='http://127.0.0.1:11434').chat(
        model="llama3.1:latest", messages=[message], stream=True
    ):
        print(part["message"]["content"], end="", flush=True)


while True:
    question = input("> Question: ")
    if question.lower() == "exit":
        break

    answer = asyncio.run(chat(question))
    print(f"\nAnswer: {answer}\n")