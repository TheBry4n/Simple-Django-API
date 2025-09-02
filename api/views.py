from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.decorators import service_injector, serializer_injector
from api.services import UserService
from api.serializers import UserSerializer, LoginSerializer

@api_view(["GET"])
@service_injector(UserService)
@serializer_injector(UserSerializer, many=True)
def user_list(request, service, serializer):
    result = service.get_user_list()
    if not result.is_success:
        return Response(result.get_error(), status=status.HTTP_400_BAD_REQUEST)
    
    user_list = result.get_data()
    serializer_data = serializer.to_representation(user_list)
    return Response(serializer_data, status=status.HTTP_200_OK)
    
@api_view(["POST"])
@service_injector(UserService)
@serializer_injector(UserSerializer)
def account_create(request, service, serializer):
    validated_data = serializer.validated_data
    result = service.account_create(validated_data)
    if not result.is_success:
        return Response(result.get_error(), status=status.HTTP_400_BAD_REQUEST)
    
    new_user = result.get_data()
    response_serializer = serializer.to_representation(new_user)
    return Response(response_serializer, status=status.HTTP_201_CREATED)

@api_view(["POST"])
@service_injector(UserService)
@serializer_injector(LoginSerializer)
def login(request, service, serializer):
    validated_data = serializer.validated_data
    result = service.login(validated_data)

    if not result.is_success:
        return Response(result.get_error(), status=status.HTTP_400_BAD_REQUEST)

    login_data = result.get_data()

    return Response({
        "message" : "Login successful",
        "access_token" : login_data["access_token"],
        "refresh_token" : login_data["refresh_token"],
        "user" : login_data["user"],
    }, status=status.HTTP_200_OK)

@api_view(["POST"])
@service_injector(UserService)
def refresh_token(request, service):
    refresh_token = request.data.get("refresh_token")
    if not refresh_token:
        return Response({"message": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    result = service.refresh_token(refresh_token)
    if not result.is_success:
        error_message = result.get_error()
        
        # If the token is revoked, return 401 instead of 400
        if "revoked" in error_message.lower():
            return Response({"message": error_message}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({"message": error_message}, status=status.HTTP_400_BAD_REQUEST)
    
    token_data = result.get_data()
    return Response({
        **token_data,
        "status" : status.HTTP_200_OK,
    })




__all__ = ["user_list", "account_create", "login", "refresh_token"]