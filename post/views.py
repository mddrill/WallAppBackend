from rest_framework.response import Response
from post.models import Post
from post.serializers import PostSerializer
from post.permissions import IsOwnerOrReadOnly, IsOwnerOrAdmin
from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied

class PostViewSet(viewsets.ModelViewSet):
    """
    Viewset for posts
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    # The default will be that anyone can read a post, but only owners can change it
    permission_classes = (IsOwnerOrReadOnly,)

    def get_permissions(self):
        # Both owners and admins can destroy a post, so if we're destroying we change permissions
        if self.action in ('destroy',):
            self.permission_classes = [IsOwnerOrAdmin, ]
        return super(self.__class__, self).get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Only authenticated users can create posts
        if request.user.is_authenticated:
            self.perform_create(serializer)
        else:
            raise PermissionDenied('Cannot post anonymously')

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)