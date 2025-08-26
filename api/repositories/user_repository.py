from django.contrib.auth.hashers import make_password  # Django use Argon2 under the hood for password hashing
from typing import Optional
from .base_repository import BaseRepository
from ..models import User

class UserRepository(BaseRepository[User]):
    
    def __init__(self):
        super().__init__(User)

    def create_user(self, user_data: dict) -> User:
        if "password" in user_data:
            user_data["password"] = make_password(user_data["password"])
        return self.create(**user_data)
    
    def update_user(self, user: User, user_data: dict) -> User:
        if "password" in user_data:
            user_data["password"] = make_password(user_data["password"])
        return self.update(user, **user_data)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.filter(email=email).first()