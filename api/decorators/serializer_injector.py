from rest_framework.response import Response
from rest_framework import status

def serializer_injector(serializer_class, many=False, instance=None):
    def decorator(view_func):
        def wrapper(request, *args):
            if request.method == "GET":
                serializer = serializer_class(many=many)
                return view_func(request, *args, serializer)
            else:
                if callable(instance):
                    instance_obj = instance(request, *args)
                else:
                    instance_obj = instance
                
                serializer = serializer_class(instance=instance_obj, data=request.data)
                if not serializer.is_valid():
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                return view_func(request, *args, serializer)
        return wrapper
    return decorator
