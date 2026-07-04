from typing import Annotated

from fastapi import Depends

from app.services.parser_service import ParserService


def get_parser_service() -> ParserService:
    return ParserService()


ParserServiceDep = Annotated[ParserService, Depends(get_parser_service)]
