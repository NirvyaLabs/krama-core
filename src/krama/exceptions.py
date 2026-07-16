"""Exception hierarchy for Krama Core."""


class KramaError(Exception):
    """Base exception for all Krama errors."""


class ConfigurationError(KramaError):
    """Raised when SDK configuration is invalid."""


class ABDMGatewayError(KramaError):
    """Raised for non-successful ABDM Gateway responses."""

    def __init__(
        self,
        status_code: int,
        message: str,
        request_id: str = "",
    ) -> None:
        self.status_code = status_code
        self.request_id = request_id
        suffix = f" request_id={request_id}" if request_id else ""
        super().__init__(f"ABDM Gateway {status_code}: {message}{suffix}")


class AuthenticationError(KramaError):
    """Raised when token acquisition or authentication fails."""


class TokenExpiredError(AuthenticationError):
    """Raised when a token cannot be refreshed before use."""


class ValidationError(KramaError):
    """Raised when caller input is invalid."""


class EncryptionError(KramaError):
    """Raised for encryption or decryption failures."""


class FHIRValidationError(KramaError):
    """Raised when a FHIR bundle fails validation."""


class TemplateNotFoundError(KramaError):
    """Raised when a clinical template cannot be found."""


class ProviderUnavailableError(KramaError):
    """Raised when an external provider is unavailable."""
