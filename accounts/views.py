from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from accounts.permissions import IsOwner, IsOwnerOrAdmin, AllowNone
from accounts.serializers import UserSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from accounts.email_info import *


global WELCOME_EMAIL_SUBJECT
global WELCOME_EMAIL_MESSAGE
global COMPANY_EMAIL

class UserViewSet(viewsets.ModelViewSet):
    """
    Viewset for accounts
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # The default will be that only owners of an account can access it
    permission_classes = [IsOwner, ]
    def get_permissions(self):

        # Anyone can create an account, so if we're creating we change permissions
        if self.action in ('create', ):
            self.permission_classes = [AllowAny, ]

        # Both owners and admins can destroy an account, so if we're destroying we change permissions
        elif self.action in ('destroy', ):
            self.permission_classes = [IsOwnerOrAdmin, ]

        # No one can list all accounts
        elif self.action in ('list', ):
            self.permission_classes = [AllowNone, ]
        return super(self.__class__, self).get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(serializer.validated_data)

            # Send email when user creates account
            email = request.data.get('email')
            send_mail(
                WELCOME_EMAIL_SUBJECT,
                WELCOME_EMAIL_MESSAGE,
                COMPANY_EMAIL,
                [email],
                fail_silently=False,
            )
            return Response('Successfully created an account', status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)