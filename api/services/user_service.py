from django.db.models import QuerySet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
import logging

from api.repositories import UserRepository
from ..models import User
from .redis_service import RedisService
from api.utils import Result

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

        token_data = {
            "access_token" : access_token,
            "refresh_token" : refresh_token,
            "user_id" : str(user.id),  # Converti UUID in stringa
            "username" : user.username,
            "created_at" : str(refresh.current_time),
        }

        # Store token in Redis
        redis_result = self.redis_service.store_token(
            str(user.id),
            token_data,
            expires_in=3600
        )

        if not redis_result.is_success:
            return Result.error(f"Failed to store tokens: {redis_result.error}")

        # Store user session in Redis
        session_data = {
            "user_id" : str(user.id),  # Converti UUID in stringa
            "username" : user.username,
            "last_login" : str(refresh.current_time),
            "is_active" : user.is_active,
        }

        session_result = self.redis_service.store_user_session(
            str(user.id),
            session_data,
            expires_in=3600
        )

        if not session_result.is_success:
            logger.warning(f"Failed to store session: {session_result.error}")
        
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
    
    def refresh_token(self, refresh_token: str) -> Result[dict] | Result[str] :
        """
        Refresh access token using refresh token
        """

        try:
            logger.info(f"Starting refresh token process for token: {refresh_token[:20]}...")
            
            # First check if the token is already blacklisted
            blacklist_check = self.redis_service.is_token_blacklisted(refresh_token)
            logger.info(f"Blacklist check result: {blacklist_check}")
            
            if blacklist_check.is_success and blacklist_check.data:
                logger.warning(f"Refresh token already blacklisted")
                return Result.error("Refresh token has been revoked")
            
            logger.info("Token not blacklisted, proceeding with refresh...")
            
            refresh = RefreshToken(refresh_token)
            user_id = refresh.payload.get("user_id")
            
            logger.info(f"Refresh token payload: {refresh.payload}")
            logger.info(f"User ID from token: {user_id}")
            
            if not user_id:
                return Result.error("Invalid refresh token")
            
            # Generate new access token
            new_access_token = str(refresh.access_token)
            
            # Generate a NEW refresh token
            new_refresh = RefreshToken()
            new_refresh['user_id'] = user_id
            new_refresh['exp'] = refresh.payload.get('exp')  # Keep the same expiration
            new_refresh_token = str(new_refresh)
            
            # INVALIDATE the old refresh token in Redis
            old_refresh_blacklist = self.redis_service.blacklist_token(
                refresh_token, 
                expires_in=604800  # 7 days (7 * 24 * 60 * 60 = 604800 seconds)
            )
            
            if not old_refresh_blacklist.is_success:
                logger.warning(f"Failed to blacklist old refresh token for user {user_id}")
            
            # Save new tokens in Redis
            token_data = {
                "access_token" : new_access_token,
                "refresh_token" : new_refresh_token,
                "user_id" : str(user_id),
                "updated_at" : str(refresh.current_time),
            }

            redis_result = self.redis_service.store_token(
                str(user_id),
                token_data,
                expires_in=3600
            )

            if not redis_result.is_success:
                return Result.error(f"Failed to store tokens: {redis_result.error}")
            
            logger.info(f"Token refreshed successfully for user {user_id}")
            
            return Result.success({
                "access_token" : new_access_token,
                "refresh_token" : new_refresh_token,
            })
        except TokenError as e:
            return Result.error(f"Invalid refresh token: {str(e)}")
        except Exception as e:
            return Result.error(f"Failed to refresh token: {str(e)}")
    
    def logout(self, user_id: str, access_token: str) -> Result[bool] | Result[str] :
        """
        Logout user and clear all tokens from Redis
        """
        try:
            # Blacklist access token in Redis
            blacklist_result = self.redis_service.blacklist_token(access_token)
            if not blacklist_result.is_success:
                logger.warning(f"Failed to blacklist access token for user {user_id}")
            
            # Get refresh token from Redis and blacklist it
            token_data_result = self.redis_service.get_token(str(user_id))
            if token_data_result.is_success:
                token_data = token_data_result.data
                refresh_token = token_data.get('refresh_token')
                
                if refresh_token:
                    refresh_blacklist_result = self.redis_service.blacklist_token(refresh_token)
                    if refresh_blacklist_result.is_success:
                        logger.info(f"Refresh token blacklisted for user {user_id}")
                    else:
                        logger.warning(f"Failed to blacklist refresh token for user {user_id}")
            
            # Clear all user data from Redis
            clear_result = self.redis_service.clear_all_user_data(str(user_id))
            if not clear_result.is_success:
                logger.warning(f"Failed to clear user data for user {user_id}")
            
            logger.info(f"User {user_id} logged out successfully")
            return Result.success(True)   
        except Exception as e:
            logger.error(f"Logout failed for user {user_id}: {str(e)}")
            return Result.error(f"Logout failed: {str(e)}")
    
    def get_user_session(self, user_id: str) -> Result[dict] | Result[str]:
        """
        Get user session from Redis
        """
        return self.redis_service.get_user_session(str(user_id))