# Resume Parser API

This project now runs as a FastAPI backend for parsing resume files and extracting structured profile data with Gemini.

## Project overview

The original Django REST Framework backend has been migrated to a production-ready FastAPI application while preserving the existing resume parsing behavior and response structure.

## Installation

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create an environment file:

   ```bash
   copy .env.example .env
   ```

4. Add your Gemini API key to `.env`.

## Environment variables

- `GEMINI_API_KEY`: API key for Gemini.
- `MODEL_NAME`: Gemini model to use.
- `ALLOWED_EXTENSIONS`: Comma-separated file extensions allowed for upload.
- `MAX_FILE_SIZE_MB`: Maximum upload size in MB.

## Running the server

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- `/docs` for Swagger UI
- `/redoc` for ReDoc

## Example API request

```bash
curl -X POST "http://127.0.0.1:8000/resume/parse" -F "file=@resume.pdf"
```

## Example API response

```json
{
  "full_name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "",
  "linkedin": "",
  "portfolio": "",
  "summary": "",
  "skills": {
    "technical": [],
    "soft": []
  },
  "education": [],
  "work_experience": [],
  "internships": [],
  "achievements": [],
  "certifications": [],
  "projects": []
}
```

## Folder structure

```text
app/
├── main.py
├── config.py
├── dependencies.py
├── schemas.py
├── utils.py
├── routers/
│   ├── __init__.py
│   └── resume.py
├── services/
│   ├── __init__.py
│   └── parser_service.py
├── models/
│   └── __init__.py
└── core/
    ├── logging.py
    └── exceptions.py
```
