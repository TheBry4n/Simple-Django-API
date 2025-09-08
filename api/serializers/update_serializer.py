from rest_framework import serializers
from ..models import User
from ..utils import PasswordUtils

class UpdateSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=False)
    confirm_password = serializers.CharField(required=False)

    def validate_username(self, value: str) -> str:
        if not value or (self.instance and self.instance.username == value):
            return value
        
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
    
    def validate_email(self, value: str) -> str:
        if not value or (self.instance and self.instance.email == value):
            return value
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        
        return value
    
    def validate_password(self, value: str) -> str:
        if not value or (self.instance and PasswordUtils.verify_password(value, self.instance.password)):
            return value
        
        is_strong, errors = PasswordUtils.is_password_strong(value)
        if not is_strong:
            raise serializers.ValidationError(errors)

        return value
    
    def validate(self, attrs: dict) -> dict:
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password and not confirm_password:
            raise serializers.ValidationError("Confirm password is required when password is provided")

        if confirm_password and not password:
            raise serializers.ValidationError("Password is required when confirm password is provided")
    
        if password and confirm_password and password != confirm_password:
            raise serializers.ValidationError("Passwords do not match")
        
        return attrs