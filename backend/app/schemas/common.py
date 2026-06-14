from typing import Any, Literal

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    status: Literal["error"]
    code: str
    message: str
    detail: Any | None = None

