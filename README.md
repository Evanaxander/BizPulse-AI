# BizPulse

BizPulse is an invoice tracking API built with FastAPI and PostgreSQL.
It extracts invoice data from images using Groq Vision, stores records in Postgres, and provides weekly expense summaries.

## Project Structure

- backend: FastAPI app, database models, and API endpoints
- openclaw-skills: OpenClaw/agent-side skill script for invoice flows
- docker-compose.yml: local PostgreSQL service

## Features

- Upload invoice images (JPEG, PNG, WebP)
- AI extraction of vendor, amount, date, currency, and items
- Persistent invoice storage in PostgreSQL
- Weekly summary endpoint for quick expense tracking
- OpenClaw skill script to connect chat flows to the API

## Prerequisites

- Python 3.10+
- Docker Desktop
- A Groq API key

## Quick Start

1. Clone the repo and move into it.
2. Start PostgreSQL via Docker.
3. Configure backend environment variables.
4. Install dependencies and run the API.

### 1) Start PostgreSQL

Run from repository root:

docker compose up -d postgres

PostgreSQL is exposed on port 5433 in this project.

### 2) Configure backend environment

Create or edit backend/.env:

DATABASE_URL=postgresql://bizpulse:bizpulse123@localhost:5433/bizpulse
GROQ_API_KEY=your_real_groq_api_key
OPENAI_API_KEY=your_openai_key_here
SECRET_KEY=your_random_secret_here

### 3) Install Python dependencies

From backend folder:

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

If requirements.txt is empty in your local copy, install the core packages manually:

pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic pydantic-settings groq pillow python-multipart

### 4) Run the API

From backend folder:

uvicorn app.main:app --reload --port 8000

### 5) Verify

Open these in a browser:

- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/docs

Note: GET / returns 404 by design unless a root route is added.

## API Endpoints

- POST /invoices/process-image
  - multipart/form-data
  - file: image file
  - uploaded_by: optional string

- GET /invoices
  - lists stored invoices

- GET /invoices/weekly-summary
  - returns last 7 days summary

- GET /health
  - health check

## OpenClaw Skill

The skill script is in openclaw-skills/invoice-ocr.js.

It calls the local API at:

http://localhost:8000

If you run the API on a different host or port, update BIZPULSE_API in that file.

## Troubleshooting

### PostgreSQL authentication failed

If you see password authentication errors:

1. Ensure backend/.env DATABASE_URL matches the docker-compose port (5433).
2. Restart DB container:

docker compose down
docker compose up -d postgres

3. Restart FastAPI server.

### openclaw command not found

In this environment, openclaw is installed as a Python library and may not provide a CLI binary.
Use your available SDK CLI or run library checks with Python imports.

## License

MIT
