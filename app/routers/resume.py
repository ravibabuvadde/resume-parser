from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.dependencies import ParserServiceDep
from app.schemas import ErrorResponse, ResumeParseResponse

router = APIRouter(tags=["resume"])


@router.post(
    "/resume/parse",
    response_model=ResumeParseResponse,
    responses={400: {"model": ErrorResponse}, 422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def parse_resume(
    file: Annotated[UploadFile, File(...)],
    parser_service: ParserServiceDep,
) -> ResumeParseResponse:
    """Parse a resume file and return structured data."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required")

    try:
        return await parser_service.parse_resume(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - service-layer failures
        raise HTTPException(status_code=500, detail=str(exc)) from exc
