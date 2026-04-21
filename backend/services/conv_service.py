from fastapi import HTTPException
import ollama
from models.response_model import ResponseModel
from modules.query_processor import get_context

class ConvService():
    def llm_response(self, query: str) -> ResponseModel:
        try:
            response, context = self._reformula(query)
            return ResponseModel(response=response, context=context)
        except :
            raise HTTPException(status_code=500, detail="The bot cannot respond your question right now. Try it later.")
        
    def _reformula(self, query: str, temperature: float = 0.0) -> str:
        context = get_context(query)

        response = ollama.chat(
            model="smollm2:latest",
            messages=[
                {
                "role": "system",
                "content": f"""
                    You are an assistant created to answer user questions based on the provided information.
                    You have access to the following inputs:

                    - **Query**: The specific question or instruction provided by the user.
                    - **Context**: Additionall contextual information that may help clarify or add details to the response: {context}

                    Your task is to use this information to provide accurate and clear answers to the user questions. When responding:

                    - Use the context to clarify or expand on the information in your response where applicable.
                    - Keep your answers concise, directly addressing the user query in a helpful manner.

                    Ensure that all responses are conversational and tailored to the user's specific needs.
                    """
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            options={
                "temperature": temperature
            }
        )

        response = response["message"]["content"]

        return response, context