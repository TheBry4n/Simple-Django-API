from rest_framework import serializers
from ..models import User
from ..utils import PasswordUtils

class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate_email(self, value: str) -> str:
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User not found")
        return value
    
    def validate(self, data: dict) -> dict:
        email = data.get("email")
        password = data.get("password")
        print(email, password)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        
        if not PasswordUtils.verify_password(password, user.password):
            raise serializers.ValidationError("User not found")
        
        data["user"] = user
        return data