from typing import TypeVar, Generic, Optional

T = TypeVar("T")

class Result(Generic[T]):
    """
    Result is a generic class that represents the result of an operation.
    Used for handling success and error cases in a functional way.
    """

    def __init__(self, data: Optional[T] = None, error: Optional[str] = None):
        self.data = data
        self.error = error
        self.is_success = error is None
    
    @classmethod
    def success(cls, data: T) -> "Result[T]":
        """Create a success result with the given data."""
        return cls(data)
    
    @classmethod
    def error(cls, error: str) -> "Result[T]":
        """Create an error result with the given error message."""
        return cls(error=error)
    
    def get_data(self) -> Optional[T]:
        """Get the data from the result."""
        return self.data
    
    def get_error(self) -> Optional[str]:
        """Get the error from the result."""
        return self.error
    
    def __bool__(self) -> bool:
        """Check if the result is successful."""
        return self.is_success
    
    def __str__(self) -> str:
        """Return a string representation of the result."""
        if self.is_success:
            return f"Success(data={self.data})"
        return f"Error(error={self.error})"