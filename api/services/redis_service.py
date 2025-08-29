from django.core.cache import cache
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from typing import Dict, Any
import json
import logging

from ..utils import Result

logger = logging.getLogger(__name__)

class RedisService:

    def __init__(self):
        self.cache = cache
        self.token_prefix = "jwt_token:"
        self.blacklist_prefix = "jwt_blacklist:"
        self.user_sessions_prefix = "user_sessions:"

    def store_token(self, user_id: str, token_data: Dict[str, Any], expires_in: int) -> Result[bool] :
        try:
            key = f"{self.token_prefix}{user_id}"
            self.cache.set(key, json.dumps(token_data), timeout=expires_in)
            return Result.success(True)
        except Exception as e:
            logger.error(f"Error storing token for user {user_id}: {str(e)}")
            return Result.error(f"Error storing token: {str(e)}")
    
    def get_token(self, user_id: str) -> Result[Dict[str, Any]] | Result[str] :
        try:
            key = f"{self.token_prefix}{user_id}"
            token_data = self.cache.get(key)

            if not token_data:
                return Result.error("Token not found")
            
            return Result.success(json.loads(token_data))
        except Exception as e:
            logger.error(f"Error getting token for user {user_id}: {str(e)}")
            return Result.error(f"Error getting token: {str(e)}")
    
    def blacklist_token(self, token: str, expires_in: int = 86400) -> Result[bool] :
        try:
            access_token = AccessToken(token)
            exp_timestamp = access_token.payload.get("exp", 0)

            import time
            current_time = int(time.time())
            remaining_time = max(exp_timestamp - current_time, expires_in)

            key = f"{self.blacklist_prefix}{token}"
            self.cache.set(key, "blacklisted", timeout=remaining_time)
            return Result.success(True)
        except TokenError as e:
            logger.error(f"Invalid token for blacklisting: {str(e)}")
            return Result.error(f"Invalid token: {str(e)}")
        except Exception as e:
            logger.error(f"Error blacklisting token: {str(e)}")
            return Result.error(f"Error blacklisting token: {str(e)}")
    
    def is_token_blacklisted(self, token: str) -> Result[bool] | Result[str] :
        try:
            key = f"{self.blacklist_prefix}{token}"
            is_blacklisted = self.cache.get(key) is not None
            return Result.success(is_blacklisted)
        except Exception as e:
            logger.error(f"Error checking token blacklist status: {str(e)}")
            return Result.error(f"Error checking token blacklist status: {str(e)}")
    
    def store_user_session(self, user_id: str, session_data: Dict[str, Any], expires_in: int = 3600) -> Result[bool] :
        try:
            key = f"{self.user_sessions_prefix}{user_id}"
            self.cache.set(key, json.dumps(session_data), timeout=expires_in)
            return Result.success(True)
        except Exception as e:
            logger.error(f"Error storing user session: {str(e)}")
            return Result.error(f"Error storing user session: {str(e)}")
        
    def get_user_session(self, user_id: str) -> Result[Dict[str, Any]] | Result[str] :
        try:
            key = f"{self.user_sessions_prefix}{user_id}"
            session_data = self.cache.get(key)

            if not session_data:
                return Result.error("Session not found")
            
            return Result.success(json.loads(session_data))
        except Exception as e:
            logger.error(f"Error getting user session: {str(e)}")
            return Result.error(f"Error getting user session: {str(e)}")
    
    def delete_user_session(self, user_id: str) -> Result[bool] :
        try: 
            key = f"{self.user_sessions_prefix}{user_id}"
            self.cache.delete(key)
            return Result.success(True)
        except Exception as e:
            logger.error(f"Error deleting user session: {str(e)}")
            return Result.error(f"Error deleting user session: {str(e)}")
    
    def clear_all_user_data(self, user_id: str) -> Result[bool] | Result[str] :
        try:
            t_key = f"{self.token_prefix}{user_id}"
            self.cache.delete(t_key)

            s_key = f"{self.user_sessions_prefix}{user_id}"
            self.cache.delete(s_key)

            return Result.success(True)
        except Exception as e:
            logger.error(f"Error clearing all user data: {str(e)}")
            return Result.error(f"Error clearing all user data: {str(e)}")