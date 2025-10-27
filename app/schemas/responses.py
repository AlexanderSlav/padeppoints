"""Standardized response models for API consistency."""
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel


T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """Base response model for all API responses."""
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None


class SuccessResponse(BaseResponse[T]):
    """Success response model."""
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    message: str
    code: Optional[str] = None
    details: Optional[dict] = None


class PaginatedResponse(BaseResponse[list[T]]):
    """Paginated response model."""
    total: int
    page: int = 1
    page_size: int = 50
    total_pages: int
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.data and self.total is not None:
            self.total_pages = max(1, (self.total + self.page_size - 1) // self.page_size)


class OperationResponse(BaseModel):
    """Response model for operations like join/leave tournament."""
    success: bool
    message: str
    data: Optional[dict] = None