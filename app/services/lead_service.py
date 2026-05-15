import re

from sqlalchemy.orm import Session

from app.models.models import Lead
from app.services.llm import llm_service


def classify_lead(message: str) -> str:
    text = message.lower()
    hot_terms = ["buy", "price", "book", "demo", "today", "urgent", "call me", "interested"]
    cold_terms = ["maybe", "later", "just checking", "not sure"]
    if any(term in text for term in hot_terms):
        return "hot"
    if any(term in text for term in cold_terms):
        return "cold"
    return "warm"


def extract_email(text: str) -> str | None:
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    return match.group(0) if match else None


def maybe_create_lead(db: Session, message: str, conversation_id: int | None, name: str | None, email: str | None) -> Lead | None:
    wants_contact = any(term in message.lower() for term in ["call", "contact", "demo", "book", "interested", "quote", "price"])
    detected_email = email or extract_email(message)
    if not wants_contact and not detected_email:
        return None

    lead_name = name or "Website Visitor"
    temperature = classify_lead(message)
    follow_up = generate_follow_up(lead_name, message, temperature)
    lead = Lead(
        name=lead_name,
        email=detected_email,
        interest=message[:1000],
        temperature=temperature,
        follow_up=follow_up,
        conversation_id=conversation_id,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def generate_follow_up(name: str, interest: str, temperature: str) -> str:
    prompt = f"Write a short follow-up message for {name}. Lead temperature: {temperature}. Interest: {interest}"
    return llm_service.complete("You write concise sales follow-up emails for small businesses.", prompt)
