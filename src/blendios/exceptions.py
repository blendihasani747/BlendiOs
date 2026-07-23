"""Domain-specific exceptions for BlendiOS."""


class BlendiOSError(Exception):
    """Base exception for all BlendiOS errors."""

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or "BLENDIOS_ERROR"


class AuthenticationError(BlendiOSError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, code="AUTHENTICATION_ERROR")


class AuthorizationError(BlendiOSError):
    """Raised when a user lacks permission."""

    def __init__(self, message: str = "Permission denied") -> None:
        super().__init__(message, code="AUTHORIZATION_ERROR")


class SessionError(BlendiOSError):
    """Raised for invalid or expired sessions."""

    def __init__(self, message: str = "Invalid or expired session") -> None:
        super().__init__(message, code="SESSION_ERROR")


class FileSystemError(BlendiOSError):
    """Raised for VFS operations."""

    def __init__(self, message: str = "File system error") -> None:
        super().__init__(message, code="FILESYSTEM_ERROR")


class ProcessError(BlendiOSError):
    """Raised for process management errors."""

    def __init__(self, message: str = "Process error") -> None:
        super().__init__(message, code="PROCESS_ERROR")


class OutOfMemoryError(BlendiOSError):
    """Raised when simulated memory is exhausted."""

    def __init__(self, message: str = "Out of memory") -> None:
        super().__init__(message, code="OUT_OF_MEMORY")


class PluginError(BlendiOSError):
    """Raised when plugin loading fails."""

    def __init__(self, message: str = "Plugin error") -> None:
        super().__init__(message, code="PLUGIN_ERROR")


class ThemeError(BlendiOSError):
    """Raised for theme-related errors."""

    def __init__(self, message: str = "Theme error") -> None:
        super().__init__(message, code="THEME_ERROR")
