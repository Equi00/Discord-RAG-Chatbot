from fastapi import HTTPException
from app_logger.logger_setup import logger
from models.feedback_model import FeedbackModel
import time
from metrics.metrics import (
    FEEDBACK_COUNT, FEEDBACK_ERROR_COUNT, 
    FEEDBACK_LATENCY, FEEDBACK_FETCH_COUNT, FEEDBACK_RETURNED_COUNT
)

class FeedbackService():
    def __init__(self, db):
        self.db = db
        self.collection = self.db["discord_bot_feedback"]

    def store_feedback(self, feedback: FeedbackModel):
        start = time.time()

        logger.info("Storing feedback", extra={
            "rating": feedback.rating,
            "step": "feedback_store"
        })

        try:
            self.collection.insert_one(feedback.model_dump())

            FEEDBACK_COUNT.labels(rating=str(feedback.rating)).inc()

            latency = int((time.time() - start) * 1000)
            FEEDBACK_LATENCY.observe(latency)

            logger.info("Feedback stored", extra={
                "step": "feedback_stored"
            })

        except Exception as e:
            FEEDBACK_ERROR_COUNT.inc()

            logger.exception("Failed to store feedback", extra={
                "step": "feedback_error"
            })

            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error, {e}"
            )
        
    def show_feedback(self) -> list[FeedbackModel]:
        start = time.time()

        FEEDBACK_FETCH_COUNT.inc()

        logger.debug("Fetching feedback list", extra={
            "step": "feedback_fetch"
        })

        feedback_data = self.collection.find({})
        feedback_list = []

        for f in feedback_data:
            f["id"] = str(f["_id"])
            del f["_id"]
            feedback_list.append(FeedbackModel(**f))

        count = len(feedback_list)

        FEEDBACK_RETURNED_COUNT.observe(count)

        latency = int((time.time() - start) * 1000)
        FEEDBACK_LATENCY.observe(latency)

        logger.info("Feedback list retrieved", extra={
            "count": count,
            "step": "feedback_fetch_done"
        })

        return feedback_list
