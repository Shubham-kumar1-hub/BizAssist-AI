# BizAssist AI

BizAssist AI is an AI-powered business assistant project made for small businesses.

The project can answer customer queries, search uploaded documents using RAG, manage leads, and automate some business workflows.

The project uses FastAPI for backend APIs, PostgreSQL for database, ChromaDB for vector search, and Streamlit for dashboard.

---

# Features

- AI chatbot for business/customer support
- Upload documents and ask questions from them
- RAG-based document search using ChromaDB
- Lead generation and lead classification
- Workflow automation
- Analytics dashboard using Streamlit
- JWT Authentication
- Docker support

---

# Tech Stack

## Backend
- FastAPI
- SQLAlchemy
- PostgreSQL

## AI & RAG
- Groq API
- ChromaDB

## Frontend / Dashboard
- Streamlit

## Deployment & Containerization
- Docker
- Docker Compose

---

# Project Structure

```text
app/
│
├── main.py              # Main FastAPI app
├── ai.py                # AI logic and RAG functions
├── auth.py              # Authentication logic
├── models.py            # Database models
├── database.py          # Database connection
├── routes/              # API routes
│
dashboard/
│
├── streamlit_app.py     # Streamlit dashboard
│
data/                    # Uploaded files / vector db data
│
Dockerfile
docker-compose.yml
README.md
```

---

# Main Functionalities

## 1. AI Chat Assistant

Users can ask business-related questions and the AI generates responses using Groq LLM.

---

## 2. Document Upload & RAG

Users can upload PDFs or text files.

The documents are:
- Split into chunks
- Stored in ChromaDB
- Retrieved during question answering

When a user asks a question, relevant chunks are searched and passed to the AI model.

---

## 3. Lead Management

The system can automatically create leads based on customer conversations.

Example:
- "I want pricing"
- "Can I book a demo?"

The project classifies leads as:
- Hot
- Warm
- Cold

---

## 4. Workflow Automation

The project supports:
- Follow-up generation
- Conversation summaries
- CSV export for CRM-like functionality

---

## 5. Dashboard

The Streamlit dashboard shows:
- Leads
- Conversations
- Analytics
- Workflow logs

---

# Architecture / Workflow

## Overall Workflow

```text
User
   ↓
FastAPI Backend
   ↓
AI Layer (Groq API)
   ↓
ChromaDB (RAG Search)
   ↓
PostgreSQL Database
   ↓
Streamlit Dashboard
```

---

# Step-by-Step Working

## 1. User Sends Message

The user sends a query to the FastAPI backend.

Example:
- "What services do you provide?"
- "Give pricing details"

---

## 2. Document Search (RAG)

The backend searches uploaded documents from ChromaDB.

Steps:
- Documents are split into chunks
- Chunks are converted into embeddings
- Relevant chunks are retrieved based on user question

---

## 3. AI Response Generation

The retrieved context and user question are sent to Groq LLM.

The AI generates the final response.

---

# Lead Detection Workflow

If the message contains words like:
- pricing
- demo
- contact
- call

then the system automatically creates a lead.

Lead types:
- Hot
- Warm
- Cold

The lead is stored in PostgreSQL database.

---

# Workflow Automation

The project also supports:
- Follow-up generation
- Conversation summary
- CRM CSV export

Workflow logs are stored in database.

---

# Dashboard Workflow

The Streamlit dashboard reads data from backend/database and displays:
- Leads
- Conversations
- Workflow logs
- Analytics

---

# Database Used

PostgreSQL is used for:
- Users
- Conversations
- Leads
- Workflow logs

---

# Vector Database Used

ChromaDB is used for:
- Document embeddings
- Semantic search
- RAG retrieval

---

# Setup Instructions

## 1. Clone Repository

```bash
git clone https://github.com/Shubham-kumar1-hub/BizAssist-AI.git
cd BizAssist-AI
```

---

## 2. Create Environment File

Create a `.env` file in root folder.

Example:

```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/bizassist
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama3-8b-8192
```

---

## 3. Run using Docker

```bash
docker-compose up --build
```

This will start:
- FastAPI backend
- PostgreSQL database
- Streamlit dashboard

---

## 4. Access Application

### FastAPI Backend
```text
http://localhost:8000
```

### Swagger Docs
```text
http://localhost:8000/docs
```

### Streamlit Dashboard
```text
http://localhost:8501
```

---

## 5. Stop Containers

```bash
docker-compose down
```

---

# Alternative Manual Setup

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Backend

```bash
uvicorn app.main:app --reload
```

## Run Streamlit Dashboard

```bash
streamlit run dashboard/streamlit_app.py
```

---

# API Endpoints

## Authentication
- `/auth/register`
- `/auth/login`

## Chat
- `/chat`

## Documents
- `/documents/upload`
- `/documents`

## Leads
- `/leads`

## Workflows
- `/workflows/run`

---

# Future Improvements

- Better embeddings model
- Real CRM integration
- LangGraph based multi-agent workflow
- Cloud deployment
- Better UI
- Real-time chat support

---

# Author

Shubham Kumar Jha
