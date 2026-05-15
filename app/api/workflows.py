from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.models import User
from app.schemas.schemas import WorkflowRequest, WorkflowResponse
from app.services.automation import run_workflow


router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/run", response_model=WorkflowResponse)
def run(payload: WorkflowRequest, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    try:
        result = run_workflow(db, payload.workflow_name, payload.payload)
        return WorkflowResponse(workflow_name=payload.workflow_name, status="success", result=result)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
