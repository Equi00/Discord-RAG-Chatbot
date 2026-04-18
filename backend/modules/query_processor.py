from openai import OpenAI
import os
import dirtyjson
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY", ""),
            )

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')


def multiquery(query: str) -> list[str]:
    response = client.chat.completions.create(
        model="google/gemma-3n-e4b-it:free",
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
                    - The result must be a readable JSON format ustin 'json.loads()' in Python, correctly formatted.

                Example of JSON output format:
                {{
                    "queries": ["query1", "query2", "query3"]
                }}
                """
            },
            {
                "role": "user",
                "content": query
            }
        ],
        temperature=0.0
    )

    queries_json = response.choices[0].message.content
    queries = dirtyjson.loads(queries_json)
    queries_list = queries["queries"]

    return queries_list


def return_context(query: str):
    embedded_query = embedding_model.encode(query)

    storage_folder = os.path.join("/backend/storage")

    faiss_db = FAISS.load_local(
        folder_path=storage_folder, 
        embeddings=embedding_model, 
        allow_dangerous_deserialization=True)
    
    context = faiss_db.similarity_search_with_score_by_vector(
        embedded_query,
        k=3,
        score_threshold = 0.8
    )

    return context


def get_context(query: str):
    queries: list[str] = multiquery(query)

    print(queries)

    full_context = []

    [full_context.append(context) 
     for query in queries 
     for context, _ in return_context(query) 
     if context not in full_context]
    
    return full_context