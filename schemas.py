from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    user_input: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)

class ChatResponse(BaseModel):
    user_input: str 
    bot_response: str
    intent: str
    session_id: str

class ResetRequest(BaseModel):
    session_id: str = Field(..., min_length=1)

class ResetResponse(BaseModel):
    message: str
    session_id: str
    request_id: str

class FeedbackRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    request_id: str = Field(..., min_length=1)
    rating: int = Field(..., ge=1, le=5)
    comments: str | None = None


class FeedbackSummaryResponse(BaseModel):
    total_feedback: int
    average_rating: float
    ratings_count: dict[str, int]
