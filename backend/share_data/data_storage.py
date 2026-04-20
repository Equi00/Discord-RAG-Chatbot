import os
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

embedding_model = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')


def extract_text_pdf(pdf_path):
    render = PdfReader(pdf_path)

    all_text = ""

    for page in render.pages:
        all_text += page.extract_text()

    return all_text


def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    chunks = text_splitter.split_text(documents)

    return [
        Document(
            page_content=chunk,
            metadata={"id": i}
        )
        for i, chunk in enumerate(chunks)
    ]


def store_documents(documents):
    storage_folder = os.path.join("storage")

    faiss_client = FAISS.from_documents(
        documents=documents, 
        embedding=embedding_model)

    faiss_client.save_local(folder_path=storage_folder)


text = extract_text_pdf(os.path.join("documents/monopoly_instructions.pdf"))

chunks = split_documents(text)

store_documents(chunks)