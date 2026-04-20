import os
import dirtyjson
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
import ollama
from concurrent.futures import ThreadPoolExecutor

embedding_model = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')

storage_folder = os.path.join("storage")

faiss_db = FAISS.load_local(
    folder_path=storage_folder, 
    embeddings=embedding_model, 
    allow_dangerous_deserialization=True)

def multiquery(query: str) -> list[str]:
    response = ollama.chat(
        model="smollm2:latest",
        messages=[
            {
            "role": "system",
            "content": f"""
                You are an assistant tasked with generating query variations.

                Given a query provided by the user, follow these steps:

                1. Generate 3 related queries, focusing on the keywords of the original query.

                2. Ensure that each new query:
                    - Is unique and relevant, without repeating the original query.
                    - Matches the format of the original query:
                        - If the original query is a question, the 3 new queries must algo be questions.
                        - If the original query is an instruction, the 3 new queries must also be instructions.

                3. Output format:
                    - The result must be a readable JSON format using 'json.loads()' in Python, correctly formatted.

                Example of JSON output format:
                {{
                    "queries": ["query1", "query2", "query3"]
                }}

                Respond in JSON format.
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

    queries_json = response["message"]["content"]
    queries = dirtyjson.loads(queries_json)
    queries_list = queries["queries"]

    return queries_list


def return_context(query: str) -> list[Document]:
    embedded_query = embedding_model.embed_query(query)
    
    context = faiss_db.similarity_search_by_vector(
        embedded_query,
        k=3
    )

    return context


def get_context(query: str) -> list[Document]:
    try:
        queries: list[str] = multiquery(query)
    except Exception as e:
        print(e)

    with ThreadPoolExecutor() as executor:
        results = list(executor.map(return_context, queries))

    full_context = []
    set_list = set()

    for sublist in results:
        for doc in sublist:
            if doc.page_content not in set_list:
                set_list.add(doc.page_content)
                full_context.append(doc)

    return full_context