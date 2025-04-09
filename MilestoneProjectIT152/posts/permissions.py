from rest_framework.permissions import BasePermission

class IsPostAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
    
class IsAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.role == 'admin'
    
class IsPostAuthor(BasePermission):
    """
    Allows access on to author of the post
    """

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
    
class IsCommentAuthor(BasePermission):
    """
    Allows access only to the author of the comment.
    """

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user