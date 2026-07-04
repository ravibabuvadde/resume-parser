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

## AWS Lambda deployment

The app runs on AWS Lambda via [Mangum](https://mangum.fastapiexpert.com/) (ASGI adapter) and [AWS SAM](https://docs.aws.amazon.com/serverless-application-model/).

### Prerequisites

- [AWS CLI](https://aws.amazon.com/cli/) configured with credentials
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- Docker (used by SAM to build the Lambda package)

### Deploy

1. Copy the example SAM config and set your Gemini API key:

   ```bash
   cp samconfig.toml.example samconfig.toml
   ```

   Edit `samconfig.toml` and replace `REPLACE_ME` in `parameter_overrides` with your `GEMINI_API_KEY`.

2. Build and deploy:

   ```bash
   sam build
   sam deploy --guided
   ```

   On first deploy, `--guided` walks through stack name, region, and parameters. Subsequent deploys can use `sam deploy` alone if `samconfig.toml` is present.

3. After deploy, SAM prints the API URL. Example:

   ```bash
   curl -X POST "https://<api-id>.execute-api.<region>.amazonaws.com/resume/parse" \
     -F "file=@resume.pdf"
   ```

### Local Lambda testing

Run the API locally with the Lambda runtime emulator:

```bash
sam build
sam local start-api --parameter-overrides GeminiApiKey=$GEMINI_API_KEY
```

Then call `http://127.0.0.1:3000/resume/parse` as usual.

### Lambda notes

- **Upload limit:** API Gateway HTTP API accepts request bodies up to **6 MB**. The SAM template defaults `MAX_FILE_SIZE_MB` to 6 for this reason. Local uvicorn can use a higher limit.
- **Timeout:** The function timeout is 120 seconds to allow Gemini API calls to complete.
- **Memory:** 1024 MB is allocated by default; increase in `template.yaml` if parsing large PDFs is slow.
- **Environment variables:** Set via SAM parameters / Lambda configuration — not from a `.env` file in the deployment bundle.

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
handler.py          # AWS Lambda entry point (Mangum)
template.yaml       # AWS SAM infrastructure template
.samignore          # Files excluded from Lambda deployment bundle
```
