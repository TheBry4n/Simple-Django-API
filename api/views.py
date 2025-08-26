from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.decorators import service_injector
from api.services import UserService
from api.serializers import UserSerializer

@api_view(["GET"])
@service_injector(UserService)
def user_list(request, service):
    user_list = service.get_user_list()
    serializer = UserSerializer(user_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



__all__ = ["user_list"]