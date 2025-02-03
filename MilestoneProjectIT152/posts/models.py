from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

# Create your models here.

#serializers.py
from rest_framework import serializers


class User(models.Model):
    username = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9_]*$',
                message='Usernames can only contain letters, numbers, and underscores')],
        unique=True)  # User's unique username
    email = models.EmailField(unique=True)  # User's unique email
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the user was created

    def __str__(self):
        return self.username


class Comment(models.Model):
    content = models.TextField(blank=False) #Required Field
    post = models.ForeignKey('Post', on_delete=models.CASCADE) #Prevent orphaned comments
    created_at = models.DateTimeField(auto_now_add=True) #Timestamp when the comment was created

    def __str__(self):
        return f"Comment on {self.post.title}: {self.content[:20]}..."
    

class Event(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def clean(self): # Custom validation
        if self.start_date >= self.end_date:
            raise ValidationError('End date must be after start date. Please adjust the dates') #Ensure that the end date is after the start date

class Post(models.Model):
    title = models.CharField(max_length=100, default='New Post')  # The title of the post
    category = models.CharField(choices=[('Tech','Tech'), ('Lifestyle', 'Lifestyle')], max_length=50, default='Tech') # The category of the post
    content = models.TextField()  # The text content of the post
    discount_percentage = models.IntegerField(default=0) # The discount percentage for the post
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)  # The user who created the post
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the post was created
    is_published = models.BooleanField(default=False)  # Whether the post is published or not

    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"

    def short_content(self):
        return self.content[:50] + '...' # Return the first 50 characters of the content


    def clean(self):
        super().clean()
        if self.discount_percentage < 0 or self.discount_percentage > 100:
            raise ValidationError('Discount percentage must be between 0 and 100') #Ensure that the discount percentage is between 0 and 100
        elif self.category == 'Tech' and self.discount_percentage > 50:
            raise ValidationError('Tech posts cannot have a discount percentage greater than 50%')
        elif self.category == 'Lifestyle' and self.discount_percentage > 30:
            raise ValidationError('Lifestyle posts cannot have a discount percentage greater than 30%')
        

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE) # The post that the like is for
    user = models.ForeignKey(User, on_delete=models.CASCADE) # The user who liked the post

    class Meta:
        unique_together = ['post', 'user'] # Ensure that a user can only like a post once

    def __str__(self):
        return f"{self.user.username} liked {self.post.title}"