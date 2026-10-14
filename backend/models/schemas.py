"""Pydantic request/response models for API validation."""
from datetime import datetime
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field


Role = Literal["student", "teacher", "admin"]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    full_name: str = Field(min_length=1, max_length=120)
    role: Role = "student"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=6, max_length=128)


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6, max_length=128)


class NotificationPrefs(BaseModel):
    quiz_reminders: bool = True
    new_uploads: bool = True
    ai_recommendations: bool = True
    milestones: bool = True


class SettingsUpdate(BaseModel):
    notification_prefs: Optional[NotificationPrefs] = None


class ChatMessageIn(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class ChatMessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime


class QuizAnswerItem(BaseModel):
    question_id: str
    answer: str


class QuizSubmit(BaseModel):
    quiz_id: str
    answers: List[QuizAnswerItem]
    duration_seconds: int = Field(ge=0, le=7200)


class BookmarkIn(BaseModel):
    material_id: str


class ProgressEventIn(BaseModel):
    subject: str
    minutes: int = Field(ge=1, le=480)
    activity_type: str = Field(default="study", max_length=40)


class WatchHistoryIn(BaseModel):
    video_id: str
    title: str
    subject: str
    youtube_id: str


class DailyChallengeComplete(BaseModel):
    challenge_id: str
