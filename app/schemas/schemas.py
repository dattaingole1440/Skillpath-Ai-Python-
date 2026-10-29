from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class UserResponse(UserBase):
    id: int
    role: str
    daily_streak: int
    quiz_avg: float
    coding_avg: float
    learning_hours: float
    profile_photo: Optional[str] = None
    current_career_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CareerBase(BaseModel):
    name: str
    description: Optional[str] = None

class CareerCreate(CareerBase):
    pass

class CareerResponse(CareerBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class QuizAnswer(BaseModel):
    question_id: int
    selected_option: str # A, B, C, D

class QuizSubmit(BaseModel):
    quiz_id: int
    answers: List[QuizAnswer]

class QuizResultResponse(BaseModel):
    score: float
    passing_percentage: int
    passed: bool
    correct_count: int
    total_questions: int
    answers_review: List[Dict[str, Any]]

class CodeSubmit(BaseModel):
    challenge_id: int
    submitted_code: str

class CodeResultResponse(BaseModel):
    status: str # passed, failed
    output: str
    score_earned: int
    test_results: List[Dict[str, Any]]

class AIRecommendationResponse(BaseModel):
    recommendation_type: str
    text_content: str
    created_at: datetime

class AnalyticsResponse(BaseModel):
    labels: List[str]
    weekly_hours: List[float]
    quiz_performance: List[float]
    coding_performance: List[float]
    topics_completed: List[int]
