from pydantic import BaseModel

class ResponseModel(BaseModel):
    response: str = ""
    context: list = []
    type: str = "Generic"