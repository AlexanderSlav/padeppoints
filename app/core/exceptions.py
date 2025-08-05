"""Custom exception classes for the application."""
from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Base exception for API-related errors."""
    
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundError(BaseAPIException):
    """Exception for resource not found errors."""
    
    def __init__(self, resource: str, identifier: str = None):
        detail = f"{resource} not found"
        if identifier:
            detail += f" with identifier: {identifier}"
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class ValidationError(BaseAPIException):
    """Exception for validation errors."""
    
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class AuthenticationError(BaseAPIException):
    """Exception for authentication errors."""
    
    def __init__(self, detail: str = "Authentication required"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(BaseAPIException):
    """Exception for authorization errors."""
    
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class ConflictError(BaseAPIException):
    """Exception for resource conflict errors."""
    
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


class TournamentError(BaseAPIException):
    """Exception for tournament-specific business logic errors."""
    
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(detail=detail, status_code=status_code)


class TournamentNotFoundError(NotFoundError):
    """Exception for tournament not found errors."""
    
    def __init__(self, tournament_id: str = None):
        super().__init__("Tournament", tournament_id)


class UserNotFoundError(NotFoundError):
    """Exception for user not found errors."""
    
    def __init__(self, user_id: str = None):
        super().__init__("User", user_id)