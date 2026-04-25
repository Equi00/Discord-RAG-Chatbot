from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.llm_router import router as llm_router
from routers.feedback_router import router as feedback_router
from app_logger.logger_setup import setup_logging
from routers.metrics_router import router as metric_router

setup_logging()

app = FastAPI(
    title="RAG chatbot",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(llm_router)
app.include_router(feedback_router)
app.include_router(metric_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Chatbot Backend!"}