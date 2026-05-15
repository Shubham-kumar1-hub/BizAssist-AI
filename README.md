# Smart AI Business Assistant Platform

This is a production-oriented MVP for the internship technical assessment. It is built for a generic small or medium business that wants one assistant to answer customer questions, capture leads, run simple automations, remember conversations, and show admin analytics.

The project is intentionally simple and easy to explain. It focuses on connected features and clean architecture instead of unnecessary complexity.

## Features

- FastAPI backend with modular routes and services
- JWT signup and login
- AI assistant powered by Groq
- Multi-turn conversation memory stored in PostgreSQL
- RAG document upload with chunking and ChromaDB vector retrieval
- Simple Planner, Executor, and Validator agent orchestration
- Natural lead capture and hot/warm/cold classification
- Three workflow automations:
  - Lead follow-up email generation
  - CRM CSV export
  - Conversation summary and next action generation
- Streamlit admin dashboard
- Analytics for leads, documents, conversations, messages, AI usage, and workflow logs
- Docker and Docker Compose support
- Fallback AI response when `GROQ_API_KEY` is not configured

## Tech Stack

- Backend: FastAPI, Python
- Dashboard: Streamlit
- Database: PostgreSQL with SQLAlchemy
- Vector store: ChromaDB
- LLM: Groq chat completions
- Auth: JWT
- Deployment: Docker

## Project Structure

```text
app/
  api/          API routes for auth, assistant, documents, leads, workflows, analytics
  core/         Configuration and security helpers
  db/           Database setup for PostgreSQL or SQLite fallback
  models/       SQLAlchemy database models
  schemas/      Pydantic request and response schemas
  services/     LLM, RAG, agents, lead capture, automation logic
  utils/        Logging setup
dashboard/      Streamlit admin dashboard
sample_docs/    Demo business document for RAG testing
data/           Local database, Chroma files, CSV exports
```

## Setup

### 1. Clone the repository

```bash
git clone <your-github-repo-link>
cd <repo-folder>
```

### 2. Create environment file

Copy `.env.example` to `.env`.

```bash
cp .env.example .env
```

Update the Groq API key:

```env
GROQ_API_KEY=your-groq-api-key
```

The default database URL uses PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/bizassist
```

For quick local testing without PostgreSQL, you can temporarily use SQLite:

```env
DATABASE_URL=sqlite:///./data/business_assistant.db
```

### 3. Start PostgreSQL

The easiest option is Docker:

```bash
docker compose up db
```

If PostgreSQL is already installed locally, create a database named `bizassist`.

### 4. Create virtual environment

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run backend

```bash
uvicorn app.main:app --reload
```

Backend will run at:

```text
http://localhost:8000
```

API docs:

```text
http://localhost:8000/docs
```

### 7. Run dashboard

Open a second terminal:

```bash
streamlit run dashboard/streamlit_app.py
```

Dashboard will run at:

```text
http://localhost:8501
```

## Docker Setup

Create `.env` first, then run:

```bash
docker compose up --build
```

Services:

- API: `http://localhost:8000`
- Dashboard: `http://localhost:8501`

## Demo Flow

1. Open the Streamlit dashboard.
2. Sign up using `admin@example.com` and `password123`.
3. Go to the Documents tab.
4. Upload `sample_docs/business_faq.txt`.
5. Go to the Assistant tab.
6. Ask:

```text
I am interested in your services. What is the pricing and can someone contact me?
```

7. The assistant answers using the uploaded document.
8. A lead is automatically created and classified as hot/warm/cold.
9. Go to the Leads tab to view the captured lead.
10. Go to Workflows and run:
    - Generate follow-up
    - Export CRM CSV
    - Summarize conversation
11. Go to Overview and Logs to show analytics and operational visibility.

## Architecture and Workflow

The platform follows a simple service-based architecture.

```mermaid
flowchart LR
    Dashboard["Streamlit Dashboard"] --> API["FastAPI Backend"]
    API --> Auth["JWT Auth"]
    API --> DB["PostgreSQL Database"]
    API --> RAG["RAG Service"]
    RAG --> Chroma["ChromaDB Vector Store"]
    API --> Agents["Planner / Executor / Validator"]
    Agents --> Groq["Groq LLM"]
    API --> Automation["Workflow Automation"]
    Automation --> Logs["Workflow Logs"]
```

### Assistant Flow

1. User sends a message from dashboard or API.
2. Backend stores the user message.
3. RAG service retrieves relevant chunks from uploaded documents.
4. Planner agent decides how to answer.
5. Executor agent generates the response using conversation memory and document context.
6. Validator agent checks whether the response is grounded.
7. Lead service checks whether the message contains buying/contact intent.
8. Backend stores the assistant response, lead data, and usage metrics.

## API Overview

Main endpoints:

- `POST /auth/signup`
- `POST /auth/login`
- `POST /assistant/chat`
- `POST /documents/upload`
- `GET /documents`
- `POST /leads`
- `GET /leads`
- `POST /workflows/run`
- `GET /analytics/summary`
- `GET /analytics/conversation-logs`
- `GET /analytics/workflow-logs`

## Reliability Features

- Fallback AI response if Groq key is missing
- Validator agent for hallucination control
- Workflow success and failure logs
- Structured service separation
- Environment-based configuration
- Dockerized deployment

## Limitations

- PostgreSQL is used for persistent records, as required in the assessment brief.
- SQLite is still supported as a fallback for quick local testing.
- The local hash embedding function is lightweight for demo use. For production, use a stronger embedding model.
- Role-based access is basic and can be expanded with admin/user permissions.
- Email sending and calendar booking are simulated as workflow outputs.

## 5-Minute Demo Video Script

1. Introduce the problem: small businesses receive many enquiries and need a simple AI assistant.
2. Show the architecture from the README.
3. Run the backend and dashboard.
4. Sign up or log in.
5. Upload the sample business FAQ document.
6. Ask a pricing/contact question in the assistant.
7. Explain RAG, memory, and the Planner/Executor/Validator agents.
8. Show the captured lead in the Leads tab.
9. Run the three workflows.
10. Show Overview analytics and Logs.
11. End by explaining limitations and future improvements.

## Future Improvements

- Hosted PostgreSQL deployment
- Real email integration
- Calendar booking integration
- Redis caching
- Streaming assistant responses
- Webhooks for CRM tools
- Better embedding model for document search
