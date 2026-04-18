from multiprocessing import get_context
from openai import OpenAI, OpenAIError
import os
from dotenv import load_dotenv

load_dotenv()

class ConvService():
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY", ""),
            )
        
    async def gpt_response(self, query: str) -> str:
        try:
            response = await self._reformula(query)
            return response
        except OpenAIError as e:
            print(e)
            raise(e)
        
    async def _reformula(self, query: str, temperature: float = 0.0) -> str:
        context = get_context(query)

        print(context)

