class DatabaseError(Exception):
    pass

class UniqueViolationError(DatabaseError):
    pass