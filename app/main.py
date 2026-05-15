from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.ai import create_lead_if_needed, run_simple_agents, run_workflow, save_document_to_vector_db, search_documents
from app.auth import check_password, create_token, get_current_user, hash_password
from app.config import settings
from app.database import Base, engine, get_db
from app.models import Conversation, Document, Lead, Message, User, WorkflowLog


Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AuthInput(BaseModel):
    email: EmailStr
    password: str


class ChatInput(BaseModel):
    message: str
    conversation_id: int | None = None
    customer_name: str | None = None
    customer_email: str | None = None


class LeadInput(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    interest: str


class WorkflowInput(BaseModel):
    workflow_name: str
    payload: dict = {}


@app.get("/")
def root():
    return {
        "message": "Smart AI Business Assistant API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/signup")
def signup(data: AuthInput, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=data.email, hashed_password=hash_password(data.password))
    db.add(user)
    db.commit()
    return {"access_token": create_token(user.email), "token_type": "bearer"}


@app.post("/auth/login")
def login(data: AuthInput, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not check_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Wrong email or password")
    return {"access_token": create_token(user.email), "token_type": "bearer"}


@app.post("/assistant/chat")
def chat(data: ChatInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    conversation = None
    if data.conversation_id:
        conversation = db.query(Conversation).filter(Conversation.id == data.conversation_id).first()

    if not conversation:
        conversation = Conversation(customer_name=data.customer_name, customer_email=data.customer_email)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    db.add(Message(conversation_id=conversation.id, sender="user", content=data.message))
    db.commit()

    context, sources = search_documents(data.message)
    old_messages = db.query(Message).filter(Message.conversation_id == conversation.id).order_by(Message.id.desc()).limit(6).all()
    memory = "\n".join(f"{msg.sender}: {msg.content}" for msg in reversed(old_messages))

    answer, validation = run_simple_agents(data.message, context, memory)
    db.add(Message(conversation_id=conversation.id, sender="assistant", content=answer))

    lead = create_lead_if_needed(db, data.message, conversation.id, data.customer_name, data.customer_email)
    conversation.summary = data.message[:300]
    db.commit()

    return {
        "conversation_id": conversation.id,
        "answer": answer,
        "validation_notes": validation,
        "sources": sources,
        "lead_created": lead is not None,
        "lead_temperature": lead.temperature if lead else None,
    }


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    content = await file.read()
    chunk_count = save_document_to_vector_db(file.filename, content)
    db.add(Document(filename=file.filename, chunk_count=chunk_count))
    db.commit()
    return {"filename": file.filename, "chunks_indexed": chunk_count}


@app.get("/documents")
def list_documents(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Document).order_by(Document.id.desc()).all()


@app.post("/leads")
def create_lead(data: LeadInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    lead = Lead(
        name=data.name,
        email=data.email,
        phone=data.phone,
        interest=data.interest,
        temperature="warm",
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@app.get("/leads")
def list_leads(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Lead).order_by(Lead.id.desc()).all()


@app.post("/workflows/run")
def workflow(data: WorkflowInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return {
        "workflow_name": data.workflow_name,
        "status": "success",
        "result": run_workflow(db, data.workflow_name, data.payload),
    }


@app.get("/analytics/summary")
def analytics_summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    lead_temperature = db.query(Lead.temperature, func.count(Lead.id)).group_by(Lead.temperature).all()
    workflow_status = db.query(WorkflowLog.status, func.count(WorkflowLog.id)).group_by(WorkflowLog.status).all()
    return {
        "total_conversations": db.query(Conversation).count(),
        "total_messages": db.query(Message).count(),
        "total_leads": db.query(Lead).count(),
        "total_documents": db.query(Document).count(),
        "lead_temperature": dict(lead_temperature),
        "workflow_status": dict(workflow_status),
    }


@app.get("/analytics/conversation-logs")
def conversation_logs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Message).order_by(Message.id.desc()).limit(100).all()


@app.get("/analytics/workflow-logs")
def workflow_logs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(WorkflowLog).order_by(WorkflowLog.id.desc()).limit(100).all()
