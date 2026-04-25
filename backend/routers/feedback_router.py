from fastapi import APIRouter, Depends
from database.database import get_db
from models.feedback_model import FeedbackModel
from services.feedback_service import FeedbackService


router = APIRouter(prefix="/api", tags=["feedback"])

def get_feedback_service(db = Depends(get_db)):
    return FeedbackService(db)


@router.get("/feedback", response_model=list[FeedbackModel])
async def show_feedback(service: FeedbackService = Depends(get_feedback_service)):
    return service.show_feedback()


@router.post("/store_feedback")
async def store_feedback(feedback: FeedbackModel, service: FeedbackService = Depends(get_feedback_service)):
    service.store_feedback(feedback)