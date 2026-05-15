# BizAssist AI

BizAssist AI is a simple AI business assistant platform for small and medium businesses. It can answer customer questions using uploaded documents, capture leads, run small automations, and show everything in an admin dashboard.

This version is intentionally kept simple so it is easy to understand and explain in a 5-minute demo.

## Main Features

- FastAPI backend
- Streamlit dashboard
- PostgreSQL database
- SQLAlchemy database models
- Groq LLM for AI responses
- ChromaDB for document search / RAG
- JWT login system
- Lead capture and hot/warm/cold classification
- Three workflow automations:
  - Lead follow-up generation
  - CRM CSV export
  - Conversation summary
- Analytics and logs dashboard
- Docker Compose setup

## Folder Structure

```text
app/
  main.py       FastAPI routes and API logic
  config.py     Loads settings from .env
  database.py   Database connection
  models.py     Database tables
  auth.py       Login, password hashing, JWT
  ai.py         Groq, RAG, lead logic, workflows

dashboard/
  streamlit_app.py  Admin dashboard

sample_docs/
  business_faq.txt  Sample file for testing document upload
```

## How The Project Works

1. Admin logs in from the dashboard.
2. Admin uploads a business document.
3. The backend reads the document and stores chunks in ChromaDB.
4. Customer asks a question.
5. The app searches relevant document chunks.
6. Groq generates an answer using the document context.
7. If the customer shows interest, the app creates a lead.
8. Admin can view leads, logs, documents, and analytics.
9. Admin can run simple automations.

## Setup

### 1. Create `.env`

Create a `.env` file in the project root:

```env
APP_NAME=BizAssist AI
SECRET_KEY=my-secret-key
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/bizassist
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.1-8b-instant
CHROMA_PATH=./data/chroma
```

For quick testing without PostgreSQL, you can temporarily use:

```env
DATABASE_URL=sqlite:///./data/business_assistant.db
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Start PostgreSQL

```bash
docker compose up db
```

### 5. Start Backend

Open another terminal:

```bash
.venv\Scripts\activate
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

API docs:

```text
http://localhost:8000/docs
```

### 6. Start Dashboard

Open another terminal:

```bash
.venv\Scripts\activate
streamlit run dashboard/streamlit_app.py
```

Dashboard:

```text
http://localhost:8501
```

## Docker Full Run

```bash
docker compose up --build
```

This starts:

- PostgreSQL on port `5432`
- FastAPI on port `8000`
- Streamlit on port `8501`

## Demo Steps

1. Open dashboard.
2. Sign up with `admin@example.com` and `password123`.
3. Upload `sample_docs/business_faq.txt`.
4. Ask:

```text
I am interested in your services. What is the pricing and can someone contact me?
```

5. Show the AI answer.
6. Show the captured lead.
7. Run the three workflows.
8. Show analytics and logs.

## Important API Endpoints

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

## Troubleshooting

If signup gives a bcrypt/passlib error:

```bash
pip uninstall bcrypt -y
pip install bcrypt==4.0.1
```

If the database does not connect, make sure PostgreSQL is running:

```bash
docker compose up db
```

## Limitations

- Email sending is simulated.
- Calendar booking is simulated.
- The embedding method is simple for demo purposes.
- SQLite fallback is only for local testing. PostgreSQL is the main database for submission.
