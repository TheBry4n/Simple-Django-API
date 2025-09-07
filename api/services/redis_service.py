from django.core.cache import cache
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from typing import Dict, Any
import json
import logging
import time

from ..utils import Result

logger = logging.getLogger(__name__)

class RedisService:

    def __init__(self):
        self.cache = cache
        self.blacklist_prefix = "jwt_blacklist:"
        self.user_sessions_prefix = "user_sessions:"

    def blacklist_token(self, token: str) -> Result[bool] | Result[str]:
        """
        Blacklists a token.
        """
        try:
            jti = self._get_jti_from_token(token)
            if not jti:
                return Result.error("Invalid token format")
            
            exp_timestamp = self._get_exp_from_token(token)
            if not exp_timestamp:
                return Result.error("Invalid token format")
            
            current_time = int(time.time())
            remaining_time = max(exp_timestamp - current_time, 0)

            key = f"{self.blacklist_prefix}{jti}"
            self.cache.set(key, "blacklisted", timeout=remaining_time)
            logger.info(f"Blacklisted refresh token by JTI: {jti}")
            return Result.success(True)

        except Exception as e:
            logger.error(f"Error blacklisting refresh token by JTI: {str(e)}")
            return Result.error(f"Error blacklisting refresh token: {str(e)}")

    def is_token_blacklisted(self, token: str) -> Result[bool] | Result[str]:
        """
        Checks if a token is blacklisted.
        """
        try:
            jti = self._get_jti_from_token(token)
            if not jti:
                return Result.error("Invalid token format")
            
            key = f"{self.blacklist_prefix}{jti}"
            is_blacklisted = self.cache.get(key) is not None
            
            return Result.success(is_blacklisted)
        except Exception as e:
            logger.error(f"Error checking token blacklist status: {str(e)}")
            return Result.error(f"Error checking token blacklist status: {str(e)}")
    
    def _get_jti_from_token(self, token: str) -> str | None:
        try:
            token_obj = RefreshToken(token)
            return token_obj.payload.get("jti")
        except TokenError:
            logger.error(f"Invalid token format: {token[:20]}...")
            return None
        except Exception as e:
            logger.error(f"Error getting JTI from token: {str(e)}")
            return None
        
    def _get_exp_from_token(self, token: str) -> int | None:
        try:
            token_obj = RefreshToken(token)
            return token_obj.payload.get("exp", 0)
        except TokenError:
            logger.error(f"Invalid token format: {token[:20]}...")
            return None
        except Exception as e:
            logger.error(f"Error getting expiration from token: {str(e)}")
            return None