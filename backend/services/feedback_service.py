from fastapi import HTTPException

from models.feedback_model import FeedbackModel


class FeedbackService():
    def __init__(self, db):
        self.db = db
        self.collection = self.db["discord_bot_feedback"]

    def store_feedback(self, feedback: FeedbackModel):
        try:
            self.collection.insert_one(feedback.model_dump())
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
        
    def show_feedback(self) -> list[FeedbackModel]:
        feedback_data = self.collection.find({})
    
        feedback_list = []

        for f in feedback_data:
            f["id"] = str(f["_id"])
            del f["_id"]

            feedback_list.append(FeedbackModel(**f))

        return feedback_list
