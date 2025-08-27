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

    return Response({"message": "Login successful"}, status=status.HTTP_200_OK)




__all__ = ["user_list", "account_create", "login"]