"""
Custom Application Exceptions (OOP Hierarchy)
Role: Member 1
Defines domain-specific error classes inheriting from a common base exception.
"""


class MemoryVaultException(Exception):
    """Base exception for all errors within the Memory Vault system."""
    def __init__(self, message: str = "An error occurred in the Memory Vault."):
        self.message = message
        super().__init__(self.message)


class DatabaseConnectionError(MemoryVaultException):
    """Raised when connecting to PostgreSQL fails."""
    pass


class UserAlreadyExistsError(MemoryVaultException):
    """Raised during registration if the email/username is already taken."""
    pass


class AuthenticationError(MemoryVaultException):
    """Raised when invalid login credentials are provided."""
    pass


class MemoryNotFoundError(MemoryVaultException):
    """Raised when attempting to access or delete a non-existent memory."""
    pass


class DocumentProcessingError(MemoryVaultException):
    """Raised when file reading, parsing, or OCR fails."""
    pass


class ValidationError(MemoryVaultException):
    """Raised when user input violates validation rules."""
    pass
