from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    status: Literal["error"]
    code: str
    message: str
    detail: Optional[Any] = None
