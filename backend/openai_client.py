import openai
import dotenv
from openai import AsyncOpenAI
dotenv.load_dotenv()

class OpenAIClient:
    def __init__(self):
        self.client = openai.OpenAI()

    def complete(self, system_prompt: str, user_prompt: str, model: str = "gpt-4o-mini", temperature: float = 0, max_tokens: int = 100) -> str:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"{{'error': '{str(e)}'}}"

class AsyncOpenAIClient:
    def __init__(self):
        self.client = openai.AsyncOpenAI()

    async def complete(self, system_prompt: str, user_prompt: str, model: str = "gpt-4o-mini", temperature: float = 0, max_tokens: int = 100) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"{{'error': '{str(e)}'}}"

    async def complete_vision(self, messages, model: str = "gpt-4o", max_tokens: int = 500, temperature: float = 0) -> str:
        """
        Send arbitrary messages (including vision/image messages) to the OpenAI API asynchronously.
        """
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip() if response.choices else None
        except Exception as e:
            return f"{{'error': '{str(e)}'}}" 