from rest_framework import serializers
from ..models import User
from ..utils import PasswordUtils

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "password", "created_at", "updated_at", "is_active"]
        read_only_fields = ["id", "created_at", "updated_at", "is_active"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def validate_password(self, value: str) -> str:
        is_strong, errors = PasswordUtils.is_password_strong(value)
        if not is_strong:
            raise serializers.ValidationError(errors)
        return value
    
    def validate_username(self, value: str) -> str:

        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long")

        if len(value) > 30:
            raise serializers.ValidationError("Username must be less than 30 characters long")

        if not value.isalnum():
            raise serializers.ValidationError("Username must be alphanumeric")

        if value.lower() == "admin":
            raise serializers.ValidationError("Username cannot be 'admin'")

        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
            
        return value
   