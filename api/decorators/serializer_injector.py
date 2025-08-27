from rest_framework.response import Response
from rest_framework import status

def serializer_injector(serializer_class, many=False):
    def decorator(view_func):
        def wrapper(request, *args):
            if request.method == "GET":
                serializer = serializer_class(many=many)
                return view_func(request, *args, serializer)
            else:
                serializer = serializer_class(data=request.data)
                if not serializer.is_valid():
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                return view_func(request, *args, serializer)
        return wrapper
    return decorator
