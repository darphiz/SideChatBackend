from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class UserCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
class UserSignInSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, data):
        try:
            user = User.objects.get(username=data['username'])
        except User.DoesNotExist as e:
            raise serializers.ValidationError({'username': 'Invalid username'}) from e
        if user and user.check_password(data['password']):
            user_token_exists = Token.objects.filter(
                user=user).exists() 
            if not user_token_exists:
                Token.objects.create(user=user)
            return user
        raise serializers.ValidationError({'password': 'Invalid password'})
    

class PasswordResetSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, data):
        user = self.context.get("request").user
        if user and user.check_password(data['old_password']):
            return data
        raise serializers.ValidationError({'old_password': 'Invalid password'})
    
    def update(self, validated_data):
        user = self.context.get("request").user
        user.set_password(validated_data['new_password'])
        user.save()
        # delete the old token
        Token.objects.filter(user=user).delete()
        Token.objects.create(user=user)
        return user
    
    
class UserSignInResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
