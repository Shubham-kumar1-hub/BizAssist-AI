from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analytics, assistant, auth, documents, leads, workflows
from app.core.config import settings
from app.db.database import Base, engine


Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(assistant.router)
app.include_router(documents.router)
app.include_router(leads.router)
app.include_router(workflows.router)
app.include_router(analytics.router)


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
