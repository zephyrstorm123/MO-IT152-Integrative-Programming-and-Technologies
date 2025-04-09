from rest_framework import serializers
from .models import User, Post, Comment, Like

class UserSerializer(serializers.ModelSerializer):
    is_verified_email = serializers.BooleanField(source='is_verified', read_only=True) # Add a read-only field to the serializer
    user_name = serializers.CharField(source='username') # Rename the username field to user_name
    password = serializers.CharField(write_only=True) # Add a write-only field for password
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='user') # Add a field for user role
    
    class Meta:
        model = User
        fields = ['id', 'user_name', 'email', 'created_at', 'is_verified_email', 'password'] # Include the new field in the serializer

    def validate_username(self, value):
        #Check if username is unique
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already exists')
        return value
    
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post']
        
class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) # Add a nested serializer for the author of the comment
    post = serializers.PrimaryKeyRelatedField(read_only=True) # Use a PrimaryKeyRelatedField to exclude the content of the post
    class Meta:
        model = Comment
        fields = ['id', 'content', 'post', 'created_at', 'user']

    def validate_post(self, value):
        #Check if referenced post exists
        if not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError('Post does not exist')
        return value
    
    # def create(self, validated_data):
    #     user = self.context['request'].user  # Get user from request context
    #     comment = Comment.objects.create(user=user, **validated_data)
    #     return comment
    
class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True) # Add a nested serializer for comments
    like_count = serializers.IntegerField(read_only=True) # Add a read-only field for the number of likes
    author = UserSerializer(read_only=True) # Add a nested serializer for the author of the post
    class Meta:
        model = Post
        fields = ['id', 'title', 'category', 'content', 'discount_percentage', 'author','created_at', 'is_published', 'comments', 'like_count']
        read_only_fields = ['author']

