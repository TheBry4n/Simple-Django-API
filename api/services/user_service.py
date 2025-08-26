from django.db.models import QuerySet

from api.repositories import UserRepository
from ..models import User


class UserService:

    def __init__(self, repo: UserRepository):
        self.repo = repo
    
    def get_user_list(self) -> QuerySet[User] :
        return self.repo.all()
