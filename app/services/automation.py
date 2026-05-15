import csv
import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.models import Lead, WorkflowLog
from app.services.llm import llm_service


def run_workflow(db: Session, workflow_name: str, payload: dict) -> dict:
    try:
        if workflow_name == "lead_followup":
            result = lead_followup(payload)
        elif workflow_name == "crm_csv_sync":
            result = crm_csv_sync(db)
        elif workflow_name == "conversation_summary":
            result = conversation_summary(payload)
        else:
            raise ValueError("Unknown workflow. Use lead_followup, crm_csv_sync, or conversation_summary.")

        log = WorkflowLog(
            workflow_name=workflow_name,
            status="success",
            input_payload=json.dumps(payload),
            output_payload=json.dumps(result),
        )
        db.add(log)
        db.commit()
        return result
    except Exception as exc:
        log = WorkflowLog(
            workflow_name=workflow_name,
            status="failed",
            input_payload=json.dumps(payload),
            error=str(exc),
        )
        db.add(log)
        db.commit()
        raise


def lead_followup(payload: dict) -> dict:
    prompt = f"Create a polite follow-up email for this lead data: {payload}"
    message = llm_service.complete("You write simple business follow-up emails.", prompt)
    return {"follow_up_email": message}


def crm_csv_sync(db: Session) -> dict:
    Path("data").mkdir(exist_ok=True)
    path = Path("data/leads_export.csv")
    leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "name", "email", "phone", "temperature", "status", "interest", "created_at"])
        for lead in leads:
            writer.writerow([lead.id, lead.name, lead.email, lead.phone, lead.temperature, lead.status, lead.interest, lead.created_at])
    return {"export_path": str(path), "lead_count": len(leads)}


def conversation_summary(payload: dict) -> dict:
    prompt = f"Summarize this conversation and suggest next tasks: {payload}"
    summary = llm_service.complete("You summarize customer conversations for business admins.", prompt)
    return {"summary": summary}
