from models.response_model import ResponseModel
from services.conv_service import ConvService
from fastapi import FastAPI, Depends


app = FastAPI()

def get_conv_service():
    return ConvService()


@app.get("/api/llm_response", response_model=ResponseModel)
def get_llm_response(query: str, service: ConvService = Depends(get_conv_service)):
    return service.llm_response(query)