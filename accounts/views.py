# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, status, permissions, serializers, viewsets
from rest_framework.generics import CreateAPIView, DestroyAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import PagePermission
from rest_framework.decorators import api_view, permission_classes
from .models import User, UserProfile, PagePermission, ActionPermission
from .serializers import (
    RegisterSerializer, UserSerializer, UserListSerializer, UserProfileSerializer,
    ProfileSerializer, ProfilePictureUploadSerializer, PagePermissionSerializer,
    ActionPermissionSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
)
from .token_serializers import CustomTokenObtainPairSerializer
from accounts.permissions import HasMinimumRole
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
import requests

ROLE_LEVELS = {
    "staff": 1,
    "finance_manager": 2,
    "operations_manager": 3,
    "md": 4,
    "admin": 5,
}

# Existing views (unchanged except for imports and ForgotPasswordView/ResetPasswordView)
class SomeProtectedView(APIView):
    permission_classes = [IsAuthenticated, HasMinimumRole]
    required_role_level = 2
    def get(self, request):
        return Response({"message": "Authorized access"})

class MeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "name": user.get_username() or user.email
        })

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

class ProfilePictureUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request, *args, **kwargs):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = ProfilePictureUploadSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "detail": "Profile image uploaded successfully.",
                "profile_image": serializer.data['profile_image']
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            if not request.user.check_password(serializer.validated_data['old_password']):
                return Response({'old_password': 'Incorrect'}, status=400)
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({'detail': 'Password changed successfully'})
        return Response(serializer.errors, status=400)

class AdminCreateUserView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RegisterSerializer
    def post(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({"detail": "Only admin users can create accounts."}, status=403)
        data = request.data.copy()
        data['password'] = 'Password10'
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully with default password 'Password10'"})
        return Response(serializer.errors, status=400)

class AdminDeleteUserView(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    lookup_field = 'id'
    def delete(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({"detail": "Only admin users can delete accounts."}, status=403)
        return super().delete(request, *args, **kwargs)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"

class PagePermissionViewSet(viewsets.ModelViewSet):
    queryset = PagePermission.objects.all()
    serializer_class = PagePermissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if "min_role" not in data:
            data["min_role"] = "staff"
        instance = PagePermission.objects.filter(page_name=data.get("page_name")).first()
        if instance:
            serializer = self.get_serializer(instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ActionPermissionViewSet(viewsets.ModelViewSet):
    queryset = ActionPermission.objects.all()
    serializer_class = ActionPermissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if "min_role" not in data:
            data["min_role"] = "staff"
        instance = ActionPermission.objects.filter(action_name=data.get("action_name")).first()
        if instance:
            serializer = self.get_serializer(instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def page_allowed(request, page_name):
    try:
        permission = PagePermission.objects.get(page_name=page_name)
        user_role = request.user.role
        if ROLE_LEVELS.get(user_role, 0) >= ROLE_LEVELS.get(permission.min_role, 0):
            return Response({"allowed": True})
        else:
            return Response({"allowed": False, "reason": f"Requires {permission.min_role} role"})
    except PagePermission.DoesNotExist:
        return Response({"allowed": False, "reason": "page_not_configured"})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def action_allowed(request, action_name: str):
    try:
        action_perm = ActionPermission.objects.get(action_name=action_name)
    except ActionPermission.DoesNotExist:
        return Response({"allowed": False, "reason": "action_not_configured"})
    user_role = getattr(request.user, "role", "staff")
    user_level = ROLE_LEVELS.get(user_role.lower(), 0)
    required_level = ROLE_LEVELS.get(action_perm.min_role.lower(), 999)
    return Response({"allowed": user_level >= required_level})

# Ensure these views are included
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                token_generator = PasswordResetTokenGenerator()
                token = token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
                webhook_data = {
                    "email": user.email,
                    "reset_url": reset_url,
                    "full_name": user.name or user.email.split('@')[0]
                }
                try:
                    response = requests.post(settings.MAKE_WEBHOOK_URL, json=webhook_data)
                    response.raise_for_status()
                    return Response({"detail": "Password reset email sent."}, status=status.HTTP_200_OK)
                except requests.RequestException as e:
                    return Response({"detail": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except User.DoesNotExist:
                return Response({"detail": "Email not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(serializer.validated_data['uid']))
                user = User.objects.get(pk=uid)
                token = serializer.validated_data['token']
                token_generator = PasswordResetTokenGenerator()
                if token_generator.check_token(user, token):
                    user.set_password(serializer.validated_data['new_password'])
                    user.save()
                    return Response({"detail": "Password reset successfully."}, status=status.HTTP_200_OK)
                return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
            except (User.DoesNotExist, ValueError):
                return Response({"detail": "Invalid user or token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)