from openai import BaseModel

class FeedbackModel(BaseModel):
    question: str = ""
    answer: str = ""
    rating: str = ""
    context: list = []
    user_id: int = 0
    message_id: int = 0
    date: str = ""