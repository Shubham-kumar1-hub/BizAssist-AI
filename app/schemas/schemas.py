from datetime import datetime

from pydantic import BaseModel, EmailStr


class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None
    customer_name: str | None = None
    customer_email: str | None = None


class ChatResponse(BaseModel):
    conversation_id: int
    answer: str
    lead_created: bool = False
    lead_temperature: str | None = None
    sources: list[str] = []
    validation_notes: str | None = None


class LeadCreate(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    interest: str


class LeadOut(BaseModel):
    id: int
    name: str
    email: str | None
    phone: str | None
    interest: str
    temperature: str
    status: str
    follow_up: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class WorkflowRequest(BaseModel):
    workflow_name: str
    payload: dict


class WorkflowResponse(BaseModel):
    workflow_name: str
    status: str
    result: dict
