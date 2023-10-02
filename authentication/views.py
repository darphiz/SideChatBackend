from rest_framework.viewsets import  ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    UserCreationSerializer,
    UserSignInResponseSerializer, 
    UserSignInSerializer, 
    PasswordResetSerializer,
)
from drf_spectacular.utils import extend_schema



# Create your views here.
@extend_schema(tags=['Authentication'])
class Authentication(ViewSet):
    def get_serializer_class(self):
        if self.action == 'signup':
            return UserCreationSerializer
        elif self.action == 'signIn':
            return UserSignInSerializer
        elif self.action == 'reset':
            return PasswordResetSerializer
        return UserCreationSerializer
    
    def get_permissions(self):
        return [IsAuthenticated(), ] if self.action == 'reset' else []
    
    @extend_schema(request=UserCreationSerializer)
    @action(methods=['POST'], detail=False)
    def signup(self, request):
        serializer = self.get_serializer_class()(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=UserSignInSerializer, responses={200: UserSignInResponseSerializer})
    @action(methods=['POST'], detail=False, url_path='login')
    def signIn(self, request):
        serializers = self.get_serializer_class()(data=request.data)
        if serializers.is_valid():
            # use reverse relationship to get the token
            token = serializers.validated_data.auth_token
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(request=PasswordResetSerializer, responses={200: UserSignInResponseSerializer})
    @action(methods=['POST'], detail=False, url_path='reset')
    def reset(self, request):
        serializers = self.get_serializer_class()(data=request.data, context={'request': request})
        if serializers.is_valid():
            data = serializers.update(serializers.validated_data)
            token = data.auth_token
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
