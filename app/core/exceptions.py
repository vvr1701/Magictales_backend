"""
Custom exception classes for the application.
"""


class ZelavoBaseException(Exception):
    """Base exception for all Zelavo errors."""

    def __init__(self, message: str, code: str, details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


class FaceValidationError(ZelavoBaseException):
    """Raised when face validation fails."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "FACE_VALIDATION_FAILED", details)


class ImageGenerationError(ZelavoBaseException):
    """Raised when AI image generation fails."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "IMAGE_GENERATION_FAILED", details)


class FaceSwapError(ZelavoBaseException):
    """Raised when face swap fails."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "FACE_SWAP_FAILED", details)


class StorageError(ZelavoBaseException):
    """Raised when storage operations fail."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "STORAGE_ERROR", details)


class WebhookVerificationError(ZelavoBaseException):
    """Raised when webhook verification fails."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "WEBHOOK_VERIFICATION_FAILED", details)


class RateLimitExceededError(ZelavoBaseException):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "RATE_LIMIT_EXCEEDED", details)


class OrderNotFoundError(ZelavoBaseException):
    """Raised when order is not found."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "ORDER_NOT_FOUND", details)


class PreviewNotFoundError(ZelavoBaseException):
    """Raised when preview is not found."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "PREVIEW_NOT_FOUND", details)


class PreviewExpiredError(ZelavoBaseException):
    """Raised when preview has expired."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "PREVIEW_EXPIRED", details)
