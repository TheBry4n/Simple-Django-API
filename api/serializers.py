from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "password", "created_at", "updated_at", "is_active"]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "password": {"write_only": True}
        }