from django.db.models import QuerySet

from api.serializers import UserSerializer
from api.repositories import UserRepository
from ..models import User

from api.utils import Result


class UserService:

    def __init__(self, repo: UserRepository):
        self.repo = repo
    
    def get_user_list(self) -> Result[QuerySet[User]] | Result[str]:
        users = self.repo.all()
        if not users:
            return Result.error("No users found")
        return Result.success(users)
    
    def account_create(self, data: dict) -> Result[User] | Result[str]:
        user = self.repo.create_user(data)
        if not user:
            return Result.error("Failed to create user")
        return Result.success(user)
    
    def login(self, data: dict) -> Result[User] | Result[str]:
        user = data.get("user")
        if not user:
            return Result.error("User not found")
        
        return Result.success(user)