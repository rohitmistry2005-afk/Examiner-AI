class AppError(Exception):
    """Base application exception."""


class ConfigurationError(AppError):
    """Raised when a required external service is not configured."""
