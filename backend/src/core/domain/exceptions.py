class DomainException(Exception):
    """Base class for all domain exceptions."""
    pass

class EntityNotFoundError(DomainException):
    """Raised when an entity is not found in the repository."""
    def __init__(self, entity_name: str, entity_id: str):
        self.message = f"{entity_name} with id {entity_id} not found."
        super().__init__(self.message)

class ValidationFailedError(DomainException):
    """Raised when domain validation rules are violated."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class UnauthorizedActionError(DomainException):
    """Raised when a user attempts an action they are not permitted to do."""
    def __init__(self, message: str = "Unauthorized action."):
        self.message = message
        super().__init__(self.message)
