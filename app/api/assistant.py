from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.models import Conversation, Message, UsageMetric, User
from app.schemas.schemas import ChatRequest, ChatResponse
from app.services.agents import agent_orchestrator
from app.services.lead_service import maybe_create_lead
from app.services.rag import rag_service


router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    if payload.conversation_id:
        conversation = db.query(Conversation).filter(Conversation.id == payload.conversation_id).first()
    else:
        conversation = None

    if not conversation:
        conversation = Conversation(customer_name=payload.customer_name, customer_email=payload.customer_email)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    db.add(Message(conversation_id=conversation.id, sender="user", content=payload.message))
    docs, sources = rag_service.search(payload.message)
    recent_messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.desc())
        .limit(8)
        .all()
    )
    memory = "\n".join(f"{message.sender}: {message.content}" for message in reversed(recent_messages))
    result = agent_orchestrator.run(payload.message, docs, memory)

    lead = maybe_create_lead(db, payload.message, conversation.id, payload.customer_name, payload.customer_email)
    db.add(Message(conversation_id=conversation.id, sender="assistant", content=result.answer))
    conversation.updated_at = datetime.utcnow()
    conversation.summary = result.plan[:1000]
    db.add(UsageMetric(feature="assistant_chat"))
    db.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        answer=result.answer,
        lead_created=lead is not None,
        lead_temperature=lead.temperature if lead else None,
        sources=list(dict.fromkeys(sources)),
        validation_notes=result.validation_notes,
    )
