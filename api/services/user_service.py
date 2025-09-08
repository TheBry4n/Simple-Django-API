from django.db.models import QuerySet
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from datetime import datetime
import logging

from api.repositories import UserRepository
from ..models import User
from .redis_service import RedisService
from api.utils import Result, PasswordUtils

logger = logging.getLogger(__name__)

class UserService:

    def __init__(self, repo: UserRepository):
        self.repo = repo
        self.redis_service = RedisService()
    
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
    
    def login(self, data: dict) -> Result[dict] | Result[str]:
        user = data.get("user")
        if not user:
            return Result.error("User not found")
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        logger.info(f"Login successful for user {user.username} with Redis")
        
        return Result.success({
            "access_token" : access_token,
            "refresh_token" : refresh_token,
            "user" : {
                "id" : str(user.id),  # Converti UUID in stringa
                "username" : user.username,
                "email" : user.email,
            }
        })
    
    def refresh_token(self, refresh_token: RefreshToken) -> Result[dict] | Result[str] :
        """
        Refresh access token using refresh token
        """
        try:
            logger.info(f"Starting refresh token process for token: {str(refresh_token)[:20]}...")
            
            # First check if the token is already blacklisted
            blacklist_check = self.redis_service.is_token_blacklisted(str(refresh_token))
            logger.info(f"Blacklist check result: {blacklist_check}")
            
            if blacklist_check.is_success and blacklist_check.data:
                logger.warning(f"Refresh token already blacklisted")
                return Result.error("Refresh token has been revoked")
            
            logger.info("Token not blacklisted, proceeding with refresh...")
            
            user_id = refresh_token.payload.get("user_id")
            if not user_id:
                return Result.error("Invalid refresh token")
            user = self.repo.get_by_id(user_id)
            if not user:
                return Result.error("User not found")

            refresh = RefreshToken.for_user(user)
            new_access_token = str(refresh.access_token)
            new_refresh_token = str(refresh)
            
            # INVALIDATE the old refresh token in Redis
            old_refresh_blacklist = self.redis_service.blacklist_token(str(refresh_token))
            if not old_refresh_blacklist.is_success:
                logger.warning(f"Failed to blacklist old refresh token for user {user_id}")
            
            logger.info(f"Token refreshed successfully for user {user_id}")
            
            return Result.success({
                "access_token" : new_access_token,
                "refresh_token" : new_refresh_token,
            })
        except TokenError as e:
            return Result.error(f"Invalid refresh token: {str(e)}")
        except Exception as e:
            return Result.error(f"Failed to refresh token: {str(e)}")
    
    def logout(self, refresh_token: RefreshToken, access_token: AccessToken) -> Result[bool] | Result[str] :
        """
        Logout user and blacklist refresh token
        """
        try:
           user_id = refresh_token.payload.get("user_id")
           if not user_id:
                return Result.error("Invalid refresh token")

           if access_token.payload.get("user_id") != user_id:
                return Result.error("Access and refresh token do not belong to the same user")

           refresh_blacklist = self.redis_service.blacklist_token(str(refresh_token))
           if not refresh_blacklist.is_success:
               return Result.error("Refresh token already blacklisted")
            
           return Result.success(True)
        except Exception as e:
           return Result.error(f"Failed to logout user: {str(e)}")

    def update_user(self, data: dict, user_id: str) -> Result[User] | Result[str]:
        user = self.repo.get_by_id(user_id)
        if not user:
            return Result.error("User not found")

        user.username = data.get("username", user.username)
        user.email = data.get("email", user.email)
        if data.get("password"):
            user.password = PasswordUtils.hash_password(data.get("password"))


        user.updated_at = datetime.now()
        user.save()
        return Result.success(user)