from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.models import Conversation, Document, Lead, Message, UsageMetric, User, WorkflowLog


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def summary(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    lead_counts = db.query(Lead.temperature, func.count(Lead.id)).group_by(Lead.temperature).all()
    workflow_counts = db.query(WorkflowLog.status, func.count(WorkflowLog.id)).group_by(WorkflowLog.status).all()
    return {
        "total_conversations": db.query(Conversation).count(),
        "total_messages": db.query(Message).count(),
        "total_leads": db.query(Lead).count(),
        "total_documents": db.query(Document).count(),
        "lead_temperature": dict(lead_counts),
        "workflow_status": dict(workflow_counts),
        "ai_usage_events": db.query(UsageMetric).count(),
    }


@router.get("/conversation-logs")
def conversation_logs(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Message).order_by(Message.created_at.desc()).limit(100).all()


@router.get("/workflow-logs")
def workflow_logs(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(WorkflowLog).order_by(WorkflowLog.created_at.desc()).limit(100).all()
