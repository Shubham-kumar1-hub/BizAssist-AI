from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.models import Lead, User
from app.schemas.schemas import LeadCreate, LeadOut
from app.services.lead_service import classify_lead, generate_follow_up


router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=LeadOut)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    temperature = classify_lead(payload.interest)
    lead = Lead(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        interest=payload.interest,
        temperature=temperature,
        follow_up=generate_follow_up(payload.name, payload.interest, temperature),
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@router.get("", response_model=list[LeadOut])
def list_leads(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Lead).order_by(Lead.created_at.desc()).all()
