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
from modules.prompt_constructor import multiquery_prompt
from dotenv import load_dotenv

load_dotenv()

client = ollama.Client(host="http://ollama:11434")

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
        response = client.chat(
            model="smollm2:latest",
            format="json",
            messages=multiquery_prompt(query),
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