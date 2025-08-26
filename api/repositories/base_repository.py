from django.db.models import QuerySet
from typing import Type, TypeVar, Optional, Generic
from ..models import User

T = TypeVar('T', bound=User)

class BaseRepository(Generic[T]):

    def __init__(self, model: Type[T]):
        self.model = model

    def create(self, **kwargs) -> T:
        return self.model.objects.create(**kwargs)
    
    def update(self, instance: T, **kwargs) -> T:
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance
    
    def delete(self, instance: T) -> None:
        instance.delete()

    def get_by_id(self, id: int) -> Optional[T]:
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None
        
    def filter(self, **kwargs) -> QuerySet[T]:
        return self.model.objects.filter(**kwargs)
    
    def exists(self, **kwargs) -> bool:
        return self.model.objects.filter(**kwargs).exists()
    
    def count(self, **kwargs) -> int:
        return self.model.objects.filter(**kwargs).count()
    
    def all(self) -> QuerySet[T]:
        return self.model.objects.all()