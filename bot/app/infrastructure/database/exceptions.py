class StateConflictError(Exception):
    """Raised when an optimistic lock fails during a database update."""
    pass
