from fastapi import HTTPException
import ollama
from models.response_model import ResponseModel
from modules.query_processor import get_context, is_valid_query
from app_logger.logger_setup import logger
import time
import uuid

class ConvService:
    def llm_response(self, query: str) -> ResponseModel:
        request_id = str(uuid.uuid4())
        start = time.time()

        logger.info("LLM request received", extra={
            "request_id": request_id,
            "query": query,
            "step": "llm_request"
        })

        if not is_valid_query(query):
            logger.warning("Invalid query", extra={
                "request_id": request_id,
                "query": query,
                "step": "validation"
            })
            return ResponseModel(
                response="Hi! I only answer Monopoly questions. Can you ask another question?"
            )

        try:
            response, context = self._reformula(query, request_id)

            latency = int((time.time() - start) * 1000)
            logger.info("LLM response generated", extra={
                "request_id": request_id,
                "query": query,
                "latency_ms": latency,
                "context_size": len(context) if context else 0,
                "response_length": len(response),
                "step": "llm_response"
            })

            return ResponseModel(response=response, context=context, type="Response")

        except Exception:
            logger.exception("LLM processing failed", extra={
                "request_id": request_id,
                "query": query,
                "step": "error"
            })
            raise HTTPException(
                status_code=500,
                detail="The bot cannot respond your question right now. Try it later."
            )

    def _reformula(self, query: str, request_id: str, temperature: float = 0.0) -> tuple[str, str]:
        rag_start = time.time()
        context = get_context(query, request_id)
        rag_latency = int((time.time() - rag_start) * 1000)

        logger.info("RAG context retrieved", extra={
            "request_id": request_id,
            "query": query,
            "latency_ms": rag_latency,
            "context_size": len(context) if context else 0,
            "step": "rag_retrieval"
        })

        prompt = f"""
            You are an assistant created to answer user questions based on the provided information.
            You have access to the following inputs:

            - **Query**: The specific question or instruction provided by the user.
            - **Context**: Additional contextual information that may help clarify or add details to the response: {context}

            Your task is to use this information to provide accurate and clear answers to the user questions. When responding:

            - Use the context to clarify or expand on the information in your response where applicable.
            - Keep your answers concise, directly addressing the user query in a helpful manner.

            Ensure that all responses are conversational and tailored to the user's specific needs.
        """

        logger.debug("Prompt built", extra={
            "request_id": request_id,
            "prompt_length": len(prompt),
            "step": "prompt_build"
        })

        llm_start = time.time()
        response = ollama.chat(
            model="smollm2:latest",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": query}
            ],
            options={"temperature": temperature}
        )
        llm_latency = int((time.time() - llm_start) * 1000)

        response_text = response["message"]["content"]

        logger.info("LLM call completed", extra={
            "request_id": request_id,
            "latency_ms": llm_latency,
            "response_length": len(response_text),
            "step": "llm_call"
        })

        return response_text, context