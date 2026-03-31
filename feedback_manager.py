import json
import os
from datetime import datetime, timezone   

class FeedbackManager:
    def __init__(self, file_path="feedback_files/feedback.json"):
        self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def load_feedback(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def save_feedback(self, feedback_entry):
        all_feedback = self.load_feedback()
        all_feedback.append(feedback_entry)

        with open(self.file_path, "w") as f:
            json.dump(all_feedback, f, indent = 2)

    def create_feedback_entry(self, session_id, request_id, rating, comments = None):
        return {
            "session_id": session_id,
            "request_id": request_id,
            "rating": rating,
            "comments": comments,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_summary(self):
        feedback_list = self.load_feedback()
        
        if not feedback_list:
            return {
                "total_feedback": 0,
                "average_rating": 0,
                "ratings_count": {
                    "1": 0,
                    "2": 0,
                    "3": 0,
                    "4": 0,
                    "5": 0
                }
            }
        
        ratings_count = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
        total_rating = 0

        for entry in feedback_list:
            rating = entry.get("rating")
            if rating in [1, 2, 3, 4, 5]:
                ratings_count[str(rating)] += 1
                total_rating += rating

        total_feedback = sum(ratings_count.values())
        average_rating = round(total_rating / total_feedback, 2) if total_feedback > 0 else 0

        return {
            "total_feedback": total_feedback,
            "average_rating": average_rating,
            "ratings_count": ratings_count
        }
