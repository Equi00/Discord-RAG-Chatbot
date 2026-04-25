import os
import json
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
import ollama
from concurrent.futures import ThreadPoolExecutor
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
from app_logger.logger_setup import logger

embedding_model = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
storage_folder = os.path.join("storage")
faiss_db = FAISS.load_local(
    folder_path=storage_folder, 
    embeddings=embedding_model, 
    allow_dangerous_deserialization=True)

model = AutoModelForSequenceClassification.from_pretrained(f"Equi00/discord-rag-chatbot")
tokenizer = AutoTokenizer.from_pretrained(f"Equi00/discord-rag-chatbot")
model.eval()


def is_valid_query(query: str) -> bool:
    inputs = tokenizer(
        query,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    with torch.no_grad():
        outputs = model(**inputs)

    preds = torch.argmax(outputs.logits, dim=1)

    return 0 == preds.tolist()[0]


def multiquery(query: str, request_id: str) -> list[str]:
    for _ in range(3):
        response = ollama.chat(
            model="smollm2:latest",
            format="json",
            messages=[
                {
                "role": "system",
                "content": """
                    You are a query generation assistant.

                    Your task is to generate exactly 3 alternative queries based on the user input.

                    STRICT RULES:
                    - Output MUST be valid JSON.
                    - Output ONLY JSON. No explanations, no extra text, no markdown.
                    - The JSON must be directly parseable with json.loads() in Python.
                    - Use double quotes (") for all keys and strings.
                    - Do NOT include trailing commas.

                    FORMAT:
                    {
                    "queries": ["query1", "query2", "query3"]
                    }

                    CONSTRAINTS:
                    - Exactly 3 queries (no more, no less)
                    - Each query must be unique
                    - Each query must preserve the intent of the original input
                    - Match the format:
                    - If the input is a question → all outputs must be questions
                    - If the input is an instruction → all outputs must be instructions

                    If you cannot comply, still return a valid JSON with 3 best-effort queries.

                    Remember: ONLY return JSON.
                    """
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            options={
                "temperature": 0.0
            }
        )

        try:
            queries_json = response["message"]["content"]
            queries: dict = json.loads(queries_json)

            if "queries" in queries:
                queries_list = []
                for question in queries["queries"]:
                    queries_list.append(question["text"])
                logger.debug("Multiquery generated", extra={
                    "request_id": request_id,
                    "query_count": len(queries_list),
                    "step": "multiquery"
                })
                return queries_list
        except:
            logger.warning("Multiquery attempt failed to parse model output", extra={
                "request_id": request_id,
                "step": "multiquery_parse"
            })
            pass

    raise ValueError("Invalid model output")


def return_context(query: str) -> list[Document]:
    embedded_query = embedding_model.embed_query(query)
    
    context = faiss_db.similarity_search_by_vector(
        embedded_query,
        k=3
    )

    return context


def get_context(query: str, request_id: str) -> list[Document]:
    queries: list[str] = multiquery(query, request_id)

    logger.debug("Context retrieval started", extra={
        "request_id": request_id,
        "query_count": len(queries),
        "step": "get_context"
    })
    
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(return_context, queries))

    full_context = []
    set_list = set()

    for sublist in results:
        for doc in sublist:
            if doc.page_content not in set_list:
                set_list.add(doc.page_content)
                full_context.append(doc)

    logger.debug("Context retrieval finished", extra={
        "request_id": request_id,
        "unique_docs": len(full_context),
        "step": "get_context_done"
    })

    return full_context