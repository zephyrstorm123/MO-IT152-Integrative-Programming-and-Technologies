from django.urls import path
from . import views
from .views import UserListCreate, PostListCreate, CommentListCreate, LikeListCreate, PostLikeView, PostCommentView, PostCommentsListView

urlpatterns = [
    # path('users/', views.get_users, name='get_users'),
    # path('users/create/', views.create_user, name='create_user'),
    # path('posts/', views.get_posts, name='get_posts'),
    # path('posts/create/', views.create_post, name='create_post'),
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('likes/', LikeListCreate.as_view(), name='like-list-create'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentListCreate.as_view(), name='comment-detail'),
    path('<int:id>/like/', PostLikeView.as_view(), name='post-like'),
    path('<int:id>/comment/', PostCommentView.as_view(), name='post-comment'),
    path('<int:id>/comments/', PostCommentsListView.as_view(), name='post-comments'),
]
