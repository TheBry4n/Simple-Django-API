from functools import wraps
from api.repositories import UserRepository

def service_injector(service_class):
    def decorate(view_func):
        @wraps(view_func)
        def wrapper(request):
            repo = UserRepository()
            service = service_class(repo)
            return view_func(request, service)
        return wrapper
    return decorate