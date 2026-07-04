import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Lambda injects env vars directly; skip .env to avoid overriding them.
if not os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    model_name: str = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    allowed_extensions: tuple[str, ...] = tuple(
        ext.strip().lower()
        for ext in os.getenv("ALLOWED_EXTENSIONS", ".pdf,.docx").split(",")
        if ext.strip()
    )
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))


def get_settings() -> Settings:
    return Settings()
