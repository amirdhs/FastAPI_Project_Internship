# FastAPI Conversation API

A FastAPI project that detects emotions from messages, generates responses, and stores conversations in a PostgreSQL database.

## Endpoints
- `POST /conversation`: Accepts a user message, detects emotion, and returns a response.

## Installation
1. Install dependencies:
   ```bash
   pip install fastapi uvicorn sqlalchemy psycopg2-binary httpx
