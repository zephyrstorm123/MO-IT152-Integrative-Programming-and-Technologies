#Imports
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from .models import User, Post
import json, logging
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import os

from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from .models import Comment, Post, Like
from .serializers import CommentSerializer, PostSerializer, UserSerializer, LikeSerializer


from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout

from rest_framework.permissions import IsAuthenticated
from .permissions import IsPostAuthor, IsAdminUser

#Authentication Imports
from rest_framework.authentication import TokenAuthentication, BasicAuthentication

#Log events
from singletons.logger_singleton import LoggerSingleton

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from factories.post_factory import PostFactory

from rest_framework.pagination import PageNumberPagination

logger = logging.getLogger('posts')  # Get an instance of a logger
logger.info('API Initialized Successfully')
# Create your views here

def get_users(request):
    try:
        users = list(User.objects.values('id', 'username', 'email', 'created_at'))
        return JsonResponse(users, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = User.objects.create(username=data['username'], email=data['email'])
            return JsonResponse({'id': user.id, 'message': 'User created successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

def get_posts(request):
    try:
        posts = list(Post.objects.values('id', 'content',
    'author', 'created_at'))
        return JsonResponse(posts, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_post(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            author = User.objects.get(id=data['author'])
            post = Post.objects.create(content=data['content'], author=author)
            return JsonResponse({'id': post.id, 'message': 'Post created successfully'}, status=201)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Author not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

class UserListCreate(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# url /posts/posts/
class PostListCreate(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)  # Set the current user as the author
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CommentListCreate(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]

    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        logger.debug(f"Request user: {request.user}")  # Log the request.user
        logger.debug(f"Request User ID: {request.user.id}")  # Log the request.user.id
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LikeListCreate(APIView):
    def get(self, request):
        likes = Like.objects.all()
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = LikeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostDetailView(APIView):
    permission_classes = [IsAuthenticated, IsPostAuthor]

    def get(self, request, pk):
        post = Post.objects.get(pk=pk)
        self.check_object_permissions(request, post)

        return Response({'content': post.content})

class ProtectedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response({'message': 'Authenticated'})
    
class CreatePostView(APIView):
    def post(self, request):
        data = request.data

        try:
            post = PostFactory.create_post(
                post_type=data['post_type'],
                title=data['title'],
                content=data.get('content', ''),
                metadata=data.get('metadata', {})
            )
            return Response({'message': 'Post created successfully!', 'post_id': post.id}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class PostLikeView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        post = get_object_or_404(Post, id=id)
        user = request.user

        if not isinstance(user, User):
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        like, created = Like.objects.get_or_create(post=post, user=user)
        if not created:
            return Response({'message': 'You have already liked this post.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Post liked successfully!'}, status=status.HTTP_201_CREATED)


#Url /posts/post/<int:id>/comment/ = allows the user to comment on the post with the given id
class PostCommentView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]

    def post(self, request, id):
        post = get_object_or_404(Post, id=id)
        logger.debug(f"Request user: {request.user}")  # Log the request.user
        logger.debug(f"Request User ID: {request.user.id}")  # Log the request.user.id
        logger.debug(f'Post: {id}')
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(post=post, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Url /posts/post/<int:id>/comments/ = shows all the comments for the certain post
class PostCommentsListView(APIView):
    def get(self, request, id):
        post = get_object_or_404(Post, id=id)
        comments = Comment.objects.filter(post=post)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

# url /posts/feed/?page_size=X = shows the latest posts in chronological order with pagination
class PostPaginationView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]


    def get(self, request):
        posts= Post.objects.all().order_by('-created_at')
        paginator = PageNumberPagination()
        paginator.page_size = request.GET.get('page_size', 5)
        page = paginator.paginate_queryset(posts, request)

        if page is not None:
            serializer = PostSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
class PostsSingleView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]

    def get(self, request, id):
        post = get_object_or_404(Post, id=id)
        # if post.privacy == 'private' and post.author != request.user:
        #     return Response({'message': 'You do not have permission to view this post.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

# urls /posts/post/<int:id>/delete/
class PostDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [BasicAuthentication]

    def delete(self, request, id):
        post = get_object_or_404(Post, id=id)
        post.delete()
        return Response({'message': 'Post deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)