from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

#Authentication Imports
from rest_framework.authentication import TokenAuthentication, BasicAuthentication

# Create your views here.
class UserLogin(APIView):
    authentication_classes = [BasicAuthentication]

    def get(self, request):
        user = request.user

        if user.is_authenticated:
            return Response({'message': 'User is authenticated', 'user': user.username}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

    @csrf_exempt
    def post(self, request):
        data = request.data
        user = authenticate(username=data['username'], password=data['password'])

        if user is not None:
            login(request, user)
            return Response({'message': 'Authentication successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserLogout(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.is_authenticated:
            logout(request)
            return Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)