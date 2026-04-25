from fastapi import HTTPException
import ollama
from dotenv import load_dotenv
from models.response_model import ResponseModel
from modules.query_processor import get_context, is_valid_query
from app_logger.logger_setup import logger
from modules.prompt_constructor import llm_prompt
import time
import uuid
from metrics.metrics import (
    REQUEST_COUNT, SUCCESS_COUNT, ERROR_COUNT,
    INVALID_QUERY_COUNT, REQUEST_LATENCY,
    RAG_LATENCY, LLM_LATENCY
)

load_dotenv()

client = ollama.Client(host="http://ollama:11434")

class ConvService:
    def llm_response(self, query: str) -> ResponseModel:
        request_id = str(uuid.uuid4())
        start = time.time()

        REQUEST_COUNT.inc()

        logger.info("LLM request received", extra={
            "request_id": request_id,
            "query": query,
            "step": "llm_request"
        })

        if not is_valid_query(query):
            INVALID_QUERY_COUNT.inc()

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

            SUCCESS_COUNT.inc()
            REQUEST_LATENCY.observe(latency)

            return ResponseModel(response=response, context=context, type="Response")

        except Exception as e:
            ERROR_COUNT.inc()
            logger.exception("LLM processing failed", extra={
                "request_id": request_id,
                "query": query,
                "step": "error"
            })
            raise HTTPException(
                status_code=500,
                detail=e
            )

    def _reformula(self, query: str, request_id: str, temperature: float = 0.0) -> tuple[str, str]:
        rag_start = time.time()
        context = get_context(query, request_id)
        rag_latency = int((time.time() - rag_start) * 1000)

        RAG_LATENCY.observe(rag_latency)

        logger.info("RAG context retrieved", extra={
            "request_id": request_id,
            "query": query,
            "latency_ms": rag_latency,
            "context_size": len(context) if context else 0,
            "step": "rag_retrieval"
        })

        prompt = llm_prompt(context)

        logger.debug("Prompt built", extra={
            "request_id": request_id,
            "prompt_length": len(prompt),
            "step": "prompt_build"
        })

        llm_start = time.time()
        response = client.chat(
            model="smollm2:latest",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": query}
            ],
            options={"temperature": temperature}
        )
        llm_latency = int((time.time() - llm_start) * 1000)

        LLM_LATENCY.observe(llm_latency)

        response_text = response["message"]["content"]

        logger.info("LLM call completed", extra={
            "request_id": request_id,
            "latency_ms": llm_latency,
            "response_length": len(response_text),
            "step": "llm_call"
        })

        return response_text, context