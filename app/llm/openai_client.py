from openai import AsyncOpenAI

from app.config import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def generate_response(message: str) -> str:
    response = await client.responses.create(
        model="gpt-5.6",
        input=message,
    )

    return response.output_text
