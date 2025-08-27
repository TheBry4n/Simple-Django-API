import os
from django.contrib.auth.hashers import make_password, check_password

class PasswordUtils:
    """
    PasswordUtils is a class that provides utility functions for password operations.
    """

    @classmethod
    def _get_pepper(cls) -> str:
        """Get the pepper from the environment variables."""
        return os.environ.get("PASSWORD_PEPPER", "")
    
    @classmethod
    def hash_password(cls, plain_password:str) -> str:
        """Hash a plain password using the pepper."""
        peppered_plain_password = f"{plain_password}{cls._get_pepper()}"
        hashed_password = make_password(peppered_plain_password)
        return hashed_password
    
    @classmethod
    def verify_password(cls, plain_password:str, hashed_password:str) -> bool:
        """Verify a plain password against a hashed password."""
        peppered_plain_password = f"{plain_password}{cls._get_pepper()}"
        return check_password(peppered_plain_password, hashed_password)
    
    @classmethod
    def is_password_strong(cls, plain_password:str) -> tuple[bool, list[str]]:
        """Check if a password is strong."""
        errors = []

        if len(plain_password) < 8 :
            errors.append("Password must be at least 8 characters long")
        
        if not any(char.isdigit() for char in plain_password):
            errors.append("Password must contain at least one digit")
        
        if not any(char.isupper() for char in plain_password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not any(char.islower() for char in plain_password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in plain_password):
            errors.append("La password deve contenere almeno un carattere speciale")
        
        return len(errors) == 0, errors