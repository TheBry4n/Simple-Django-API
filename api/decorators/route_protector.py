from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken, TokenError

def route_protector(required=False):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args):
            auth_header = request.META.get("HTTP_AUTHORIZATION")
            if not auth_header or not auth_header.startswith("Bearer "):
                return Response({"message": "Invalid authorization header"}, status=status.HTTP_401_UNAUTHORIZED)
            
            token_str = auth_header.split(" ")[1]
            try:
                token_obj = AccessToken(token_str)
            except TokenError:
                return Response({"message": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            
            if required:
                return view_func(request, *args, token_obj)
            else:
                return view_func(request, *args)
        return wrapper
    return decorator


