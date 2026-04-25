from fastapi import HTTPException
from app_logger.logger_setup import logger
from models.feedback_model import FeedbackModel


class FeedbackService():
    def __init__(self, db):
        self.db = db
        self.collection = self.db["discord_bot_feedback"]

    def store_feedback(self, feedback: FeedbackModel):
        logger.info("Storing feedback", extra={
            "rating": feedback.rating,
            "step": "feedback_store"
        })

        try:
            self.collection.insert_one(feedback.model_dump())

            logger.info("Feedback stored", extra={
                "step": "feedback_stored"
            })
        except Exception as e:
            logger.exception("Failed to store feedback", extra={
                "step": "feedback_error"
            })
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
        
    def show_feedback(self) -> list[FeedbackModel]:
        logger.debug("Fetching feedback list", extra={
            "step": "feedback_fetch"
        })
        
        feedback_data = self.collection.find({})
    
        feedback_list = []

        for f in feedback_data:
            f["id"] = str(f["_id"])
            del f["_id"]

            feedback_list.append(FeedbackModel(**f))

        logger.info("Feedback list retrieved", extra={
            "step": "feedback_fetch_done"
        })

        return feedback_list
