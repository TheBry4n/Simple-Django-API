from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

def extract_refresh_token():
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args):
            token_str = request.META.get("HTTP_X_REFRESH_TOKEN")
            if not token_str:
                return Response({"message": "Invalid refresh header"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                token_obj = RefreshToken(token_str)
            except TokenError:
                return Response({"message": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)
            
            return view_func(request, *args, refresh_token=token_obj)
        return wrapper
    return decorator