import csv
import hashlib
import json
import math
import re
from pathlib import Path
from uuid import uuid4

import chromadb
from chromadb.api.types import EmbeddingFunction
from groq import Groq
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Lead, WorkflowLog


class SimpleEmbedding(EmbeddingFunction):
    def __call__(self, input):
        return [self.make_vector(text) for text in input]

    def make_vector(self, text: str, size: int = 256) -> list[float]:
        vector = [0.0] * size
        for word in text.lower().split():
            index = int(hashlib.md5(word.encode()).hexdigest(), 16) % size
            vector[index] += 1.0
        length = math.sqrt(sum(x * x for x in vector)) or 1.0
        return [x / length for x in vector]


Path(settings.chroma_path).mkdir(parents=True, exist_ok=True)
chroma_client = chromadb.PersistentClient(path=settings.chroma_path)
documents_collection = chroma_client.get_or_create_collection(
    name="business_docs",
    embedding_function=SimpleEmbedding(),
)


def ask_groq(system_prompt: str, user_prompt: str) -> str:
    if not settings.groq_api_key:
        return "Demo AI response. Add GROQ_API_KEY in .env to get real Groq answers."

    client = Groq(api_key=settings.groq_api_key)
    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=600,
    )
    return response.choices[0].message.content or ""


def split_text(text: str, size: int = 800) -> list[str]:
    clean_text = " ".join(text.split())
    return [clean_text[i : i + size] for i in range(0, len(clean_text), size) if clean_text[i : i + size].strip()]


def read_file_text(filename: str, content: bytes) -> str:
    if filename.lower().endswith(".pdf"):
        temp_file = Path("data") / f"temp_{Path(filename).name}"
        temp_file.parent.mkdir(exist_ok=True)
        temp_file.write_bytes(content)
        reader = PdfReader(str(temp_file))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        temp_file.unlink(missing_ok=True)
        return text
    return content.decode("utf-8", errors="ignore")


def save_document_to_vector_db(filename: str, content: bytes) -> int:
    text = read_file_text(filename, content)
    chunks = split_text(text)
    if not chunks:
        return 0

    upload_id = uuid4().hex[:8]
    documents_collection.add(
        ids=[f"{filename}-{upload_id}-{i}" for i in range(len(chunks))],
        documents=chunks,
        metadatas=[{"filename": filename} for _ in chunks],
    )
    return len(chunks)


def search_documents(question: str) -> tuple[str, list[str]]:
    result = documents_collection.query(query_texts=[question], n_results=3)
    chunks = result.get("documents", [[]])[0]
    sources = [item.get("filename", "document") for item in result.get("metadatas", [[]])[0]]
    return "\n\n".join(chunks), list(dict.fromkeys(sources))


def run_simple_agents(question: str, context: str, memory: str) -> tuple[str, str]:
    plan = ask_groq(
        "You are a simple planner agent.",
        f"Question: {question}\nContext: {context}\nWrite a short plan for answering.",
    )

    answer = ask_groq(
        "You are a helpful business assistant. Use the context. If context is missing, say so.",
        f"Plan: {plan}\nConversation memory: {memory}\nBusiness context: {context}\nCustomer question: {question}",
    )

    validation = ask_groq(
        "You are a validator agent.",
        f"Check this answer in one short line.\nContext: {context}\nAnswer: {answer}",
    )
    return answer, validation


def classify_lead(text: str) -> str:
    lower_text = text.lower()
    if any(word in lower_text for word in ["buy", "price", "demo", "call", "urgent", "book"]):
        return "hot"
    if any(word in lower_text for word in ["maybe", "later", "just checking"]):
        return "cold"
    return "warm"


def find_email(text: str) -> str | None:
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    return match.group(0) if match else None


def create_lead_if_needed(db: Session, message: str, conversation_id: int, name: str | None, email: str | None) -> Lead | None:
    contact_words = ["price", "demo", "call", "contact", "interested", "quote", "book"]
    should_create = any(word in message.lower() for word in contact_words) or find_email(message)
    if not should_create:
        return None

    lead_name = name or "Website Visitor"
    lead_email = email or find_email(message)
    temperature = classify_lead(message)
    follow_up = ask_groq(
        "Write short business follow-up emails.",
        f"Write a follow-up for {lead_name}. Interest: {message}. Lead type: {temperature}",
    )

    lead = Lead(
        name=lead_name,
        email=lead_email,
        interest=message,
        temperature=temperature,
        follow_up=follow_up,
        conversation_id=conversation_id,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def run_workflow(db: Session, name: str, payload: dict) -> dict:
    if name == "lead_followup":
        result = {"follow_up": ask_groq("Write follow-up emails.", json.dumps(payload))}
    elif name == "crm_csv_sync":
        leads = db.query(Lead).all()
        Path("data").mkdir(exist_ok=True)
        path = Path("data/leads_export.csv")
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["id", "name", "email", "temperature", "interest"])
            for lead in leads:
                writer.writerow([lead.id, lead.name, lead.email, lead.temperature, lead.interest])
        result = {"file": str(path), "leads_exported": len(leads)}
    elif name == "conversation_summary":
        result = {"summary": ask_groq("Summarize business conversations.", json.dumps(payload))}
    else:
        raise ValueError("Unknown workflow")

    db.add(WorkflowLog(workflow_name=name, status="success", details=json.dumps(result)))
    db.commit()
    return result
