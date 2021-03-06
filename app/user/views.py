from rest_framework import generics
from .serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Create user"""
    serializer_class = UserSerializer
