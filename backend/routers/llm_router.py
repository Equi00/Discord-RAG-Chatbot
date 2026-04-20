from fastapi import Depends, APIRouter
from models.response_model import ResponseModel
from services.conv_service import ConvService

router = APIRouter(prefix="/api", tags=["llm"])

def get_conv_service():
    return ConvService()


@router.get("/api/llm_response", response_model=ResponseModel)
def get_llm_response(query: str, service: ConvService = Depends(get_conv_service)):
    return service.llm_response(query)