from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import ResumeProcessingError
from app.routers.resume import router as resume_router

app = FastAPI(
    title="Resume Parser API",
    version="1.0.0",
    description="FastAPI backend for extracting structured resume data.",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(resume_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Simple health endpoint for service checks."""
    return {"status": "ok"}


@app.exception_handler(ResumeProcessingError)
async def resume_processing_error_handler(_: Request, exc: ResumeProcessingError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.errors()})
